from flask import Flask 
from routes import routes_blueprint
from Project.Engine.engine import Engine
import threading
import time
from kafka import KafkaProducer

app = Flask(__name__)
app.engine = Engine()  # Initialiser l'engine

# Lancer le jeu dans un thread séparé
def run_game():
    while not app.engine.isReadyToStart():
        time.sleep(1)
    try:
        app.engine.run()
        print('Run Game !')
    except Exception as e:
        print(str(e))

# Démarrer le thread du jeu
game_thread = threading.Thread(target=run_game, daemon=True)
game_thread.start()

# Enregistrer le blueprint des routes
app.register_blueprint(routes_blueprint)


# Kafka configuration
KAFKA_BROKER = 'localhost:9092'  # Adresse de votre broker Kafka
KAFKA_TOPICS = {
    'enter_arena': 'enter_arena_topic',
    'gold': 'gold_topic',
    'set_action': 'set_action_topic',
    'damage': 'damage_topic',
    'death': 'death_topic',
    'set_target': 'set_target_topic',
    'turn_id': 'turn_id_topic',
    'start_game': 'start_game_topic',
}
app.config['KAFKA_TOPICS'] = KAFKA_TOPICS

# Kafka Producer initialization
kafka_producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=None
)
app.kafka_topics = KAFKA_TOPICS
app.kafka_producer = kafka_producer
app.config['KAFKA_PRODUCER'] = kafka_producer


if __name__ == '__main__':
    app.run(debug=False, port=6969, host="0.0.0.0")

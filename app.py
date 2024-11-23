from flask import Flask 
from routes import routes_blueprint
from Project.Engine.engine import Engine
import threading
import time

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

if __name__ == '__main__':
    app.run(debug=False)

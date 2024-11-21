from flask import Flask
from routes import routes_blueprint
from Project.Engine.engine import Engine

app = Flask(__name__)
app.engine = Engine()

app.register_blueprint(routes_blueprint)

if __name__ == '__main__':
    app.run(debug=True)


def run_game():
    while not engine.isReadyToStart():
        time.sleep(1)
    try:
        engine.run()
    except Exception as e:
        print(str(e))
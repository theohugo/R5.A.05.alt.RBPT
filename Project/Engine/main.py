from flask import Flask
from character import *
from engine import *
import threading
import time

app = Flask(__name__)
engine = Engine()

def run_game():
    while not engine.isReadyToStart():
        time.sleep(1)
    try:
        engine.run()
    except Exception as e:
        print(str(e))

from flask import Flask
from character import *
from engine import *
import threading
import time

app = Flask(__name__)
engine = Engine()

@app.route('/getCharacter/<cid>')
def get_character(cid):
    a = engine.getPlayerByName(cid)
    if a is None:
        pass
    return "<p> character : " + str(a) + "</p>"

@app.route('/enterArena/<cid>/<teamid>/<life>/<strength>/<armor>/<speed>')
def enter_arena(cid, teamid, life, strength, armor, speed):
    a = CharacterProxy(cid, teamid, int(life), int(strength), int(armor), int(speed))
    engine.addPlayer(a)
    return "<p> enter arena : " + str(a) + "</p>"

@app.route('/setAction/<cid>/<action>')
def set_action(cid, action):
    flag = engine.setActionTo(cid, int(action))
    if flag:
        return "<p> action is " + str(action) + "</p>"
    return "<p> action error : " + str(flag) + "</p>"

@app.route('/setTarget/<cid>/<target>')
def set_target(cid, target):
    flag = engine.setTargetTo(cid, target)
    if flag:
        return "<p> target is " + str(target) + "</p>"
    return "<p> target error : " + str(flag) + "</p>"

@app.route('/singleRun')
def single_run():
    try:
        engine.single_run()
    except Exception as e:
        return "<p>" + str(e) +  "</p>"
    return "<p> ok </p>"

def run_game():
    while not engine.isReadyToStart():
        time.sleep(1)
    try:
        engine.run()
    except Exception as e:
        print(str(e))

@app.route('/run')
def run():
    x = threading.Thread(target=run_game)
    x.start()
    return "<p> game is running </p>"

@app.route('/getArenaState')
def getState():
    return engine.getState()
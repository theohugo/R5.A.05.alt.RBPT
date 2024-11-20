from flask import Flask, jsonify, request, render_template, abort
import json
from character import *
from engine import *
from arena import *
from http import *
import http.client


app = Flask(__name__)

# Fonctions utilitaires
@app.route('/')
def index():
    return "Home page"

# ---------------------------------- Routes prof ----------------------------------

# - GET - /character/id/ - récupérer un personnages - cid
@app.route('/character/<character_id>', methods=['GET'])
def get_character(character_id):
    arena = Arena(engine._arena)
    characters = arena._playersList
    for character in characters:
        if character.isId(character_id):
            return jsonify(character, 200)
    return jsonify({"error": "Personnage non trouvé"}), 404

# - GET - /characters/ - récupéré les personnages d'une arène
@app.route('/characters/', methods=['GET'])
def get_characters():
    arena = Arena(engine._arena)
    return jsonify(arena._playersList,200)

# # - POST - /character/join/ - ajouter un personnage à une arène - cid, teamid, life, strength, armor, speed
@app.route('/character/join', methods=['POST'])
def join_character():
    character_id = request.json.get('characterId')

    for characters in engine._arena._playersList:
        if character in characters:
            character = get_character(character_id)
            _ = http.client.HTTPSConnection("ADDRESS").request("POST", "/character/join", character)
            engine._arena.removePlayer(character)
            return jsonify({"message": "Personnage server switch"}), 200
    
    character = CharacterProxy(character_id, request.json.get('teamId'), request.json.get('life'), request.json.get('strength'), request.json.get('armor'), request.json.get('speed'))
    engine._arena.addPlayer(character)
    return jsonify({"message": "Personnage ajouté"}), 200

#- POST - /character/<character_id>/action/<action_id>/target - ajouter une action à un personnage - cid, action, target
@app.route('/character/action/<character_id>/<action_id>/<target_id>', methods=['GET'])
def action_character(character_id,action_id,target_id):
    dataCharacters = get_character(character_id)
    dataTarget = get_character(target_id)
    character = CharacterProxy(character_id, dataCharacters["teamId"], dataCharacters["life"], dataCharacters["strength"], dataCharacters["armor"], dataCharacters["speed"])
    target = CharacterProxy(target_id, dataTarget["teamId"], dataTarget["life"], dataTarget["strength"], dataTarget["armor"], dataTarget["speed"])
    if(target):
        character.setTarget(target.getId())
    if action_id == actionToStr(ACTION.HIT):
        character.setAction(ACTION.HIT)
        return jsonify({"message": "Personnage ajouté"}), 200
    elif action_id == actionToStr(ACTION.BLOCK):
        character.setAction(ACTION.BLOCK)
        return jsonify({"message": "Personnage ajouté"}), 200
    elif action_id == actionToStr(ACTION.DODGE):
        character.setAction(ACTION.DODGE)
        return jsonify({"message": "Personnage ajouté"}), 200
    elif action_id == actionToStr(ACTION.FLY):
        character.setAction(ACTION.FLY)
        return jsonify({"message": "Personnage ajouté"}), 200
    else:
        return jsonify({"error": "Action non trouvée"}), 404

# POST - /character/action/switcharena/<character_id>/<arena_id>
@app.route('/character/action/switcharena/<character_id>/<arena_id>', methods=['POST'])
def switch_arena(character_id, arena_id):
    
    character_data = get_character(character_id) 
    if 'error' in character_data:
        return jsonify(character_data), 404
    
    new_arena_url = select_new_arena(arena_id) 
    
    response = send_to_arena(new_arena_url, character_data)
    
    if response.status == 200:
        return jsonify({
            "message": "Personnage transféré avec succès.",
            "new_arena_url": new_arena_url
        }), 200
    else:
        return jsonify({"error": "Erreur lors du transfert de personnage."}), 500

def select_new_arena(arena_id):
    arenas = {
        '1': "arena1-address",
        '2': "arena2-address",
        '3': "arena3-address",
        '4': "arena4-address"
    }
    return arenas.get(arena_id, "default-arena-address")

def send_to_arena(url, character_data):
    conn = http.client.HTTPSConnection(url)
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(character_data)
    conn.request("POST", "/character/join", body=json_data, headers=headers)
    return conn.getresponse()


# Démarrer le serveur
if __name__ == '__main__':
    engine = Engine()
    app.run(debug=True)
    engine.run()

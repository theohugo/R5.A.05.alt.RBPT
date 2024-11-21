
import time, json
from http import *
import http.client
from Project.Engine.data import *
from Project.Engine.arena import *
from Project.Engine.character import *
from app import app
from flask import Flask, jsonify, request

arena_networks = {
    1: {"arena_network": "192.168.10.1"},
    2: {"arena_network": "192.168.10.2"}
}

characters = [
    {
        "cid": 1,
        "team_id": 1,
        "arena_id": 2,
        "life": 5,
        "strength": 3,
        "armor": 3,
        "speed": 2
    },
    {
        "cid": 2,
        "team_id": 2,
        "arena_id": 2,
        "life": 8,
        "strength": 23,
        "armor": 34,
        "speed": 25
    },
    {
        "cid": 3,
        "team_id": 1,
        "arena_id": 2,
        "life": 80,
        "strength": 30,
        "armor": 50,
        "speed": 10
    }
]

matches = [
    {"id": 1, "title": "Learn Flask", "done": False},
    {"id": 2, "title": "Build an API", "done": False}
]

@app.get('/')
def say_hello():
    return {'message': 'Hello!'}

# GET - récupérer les personnages d'une arène - /characters/
@app.route('/characters/', methods=['GET'])
def get_characters():
    arena = engine._arena
    characters = arena._playersList
    return jsonify({"characters" : characters}), 200

# GET - récupérer les résultats des matchs /status/ - numéro de tour
@app.route('/status/', methods=['GET'])
def get_matches():
    return jsonify({"matches": matches})

# GET - récupérer un personnage - /character/<cid>
@app.route('/character/<int:cid>', methods=['GET'])
def get_character(cid):
    character = next((character for character in characters if character["cid"] == cid), None)
    if character is None:
        return jsonify({"error": "character not found"}), 404
    return jsonify(character)

# POST - ajouter un personnage à une arène - /character/join/
@app.route('/character/join/', methods=['POST'])
def create_character():
    if not request.json or "arena_id" not in request.json:
        return jsonify({"error": "Bad Request"}), 400

    arena_id = request.json["arena_id"]
    if arena_id not in arena_networks:
        return jsonify({"error": "Invalid Arena ID"}), 400

    # Générer un cid unique
    new_cid = max([char["cid"] for char in characters], default=0) + 1

    new_character = {
        "cid": new_cid,
        "team_id": request.json["team_id"],
        "arena_id": request.json["arena_id"],
        "life": request.json["life"],
        "strength": request.json["strength"],
        "armor": request.json["armor"],
        "speed": request.json["speed"]
    }

    characters.append(new_character)
    return jsonify(new_character), 201

# PUT - mettre à jour un personnage - /character/<cid>
@app.route('/character/<int:cid>', methods=['PUT'])
def update_character(cid):
    character = next((character for character in characters if character["cid"] == cid), None)

    if character is None:
        return jsonify({"error": "character not found"}), 404
    if not request.json:
        return jsonify({"error": "Bad Request"}), 400

    character["arena_id"] = request.json.get("arena_id", character["arena_id"])

    return jsonify(character)

# DELETE - supprimer un personnage - /character/<cid>
@app.route('/character/<int:cid>', methods=['DELETE'])
def delete_character(cid):
    global characters
    character = next((character for character in characters if character["cid"] == cid), None)
    if character is None:
        return jsonify({"error": "character not found"}), 404
    characters = [char for char in characters if char["cid"] != cid]
    return jsonify({"message": f"Character with cid {cid} has been deleted."}), 200

# POST - /character/action/switcharena/<character_id>/<arena_id>
@app.route('/character/action/switcharena/<int:character_id>/<int:arena_id>', methods=['POST'])
def switch_arena(character_id, arena_id):
    character_response = get_character(character_id)
    character_data = character_response.get_json()
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
    return arena_networks[arena_id]['arena_network']

def send_to_arena(url, character_data):
    import http.client
    import json
    host = url.split('//')[1]  # Extraire l'hôte de l'URL
    conn = http.client.HTTPConnection(host)
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(character_data)
    conn.request("POST", "/character/join/", body=json_data, headers=headers)
    return conn.getresponse()
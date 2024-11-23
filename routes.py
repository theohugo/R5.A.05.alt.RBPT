import time, json
import http.client
from Project.Engine.data import *
from Project.Engine.arena import *
from Project.Engine.character import *
from flask import current_app, jsonify, request, Blueprint
import uuid

# Créer un Blueprint pour enregistrer les routes dans app.py
routes_blueprint = Blueprint('routes', __name__)

arena_networks = {
    1: {"arena_network": "192.168.10.1"},
    2: {"arena_network": "192.168.10.2"}
}

matches = [
    {"id": 1, "title": "Learn Flask", "done": False},
    {"id": 2, "title": "Build an API", "done": False}
]

# GET - dire bonjour
@routes_blueprint.route('/', methods=['GET'])
def say_hello():
    return {'message': 'Hello!'}

# GET - récupérer les personnages d'une arène - /characters/
@routes_blueprint.route('/characters/', methods=['GET'])
def get_characters():
    arena = current_app.engine._arena
    characters = arena._playersList
    return jsonify({"characters": [char.toDict() for char in characters]}), 200

# GET - récupérer les résultats des matchs /status/ - numéro de tour
@routes_blueprint.route('/status/', methods=['GET'])
def get_engine_status():
    engine = current_app.engine
    turn = engine._turnId  
    active_players = engine._arena.getActiveNbPlayer()
    return jsonify({
        "turn": turn,
        "active_players": active_players
    }), 200

# GET - récupérer un personnage - /character/<cid>
@routes_blueprint.route('/character/join/', methods=['POST'])
def create_character():
    if not request.json:
        return jsonify({"error": "Request body is missing"}), 400

    required_fields = ["team_id", "arena_id", "life", "strength", "armor", "speed"]
    for field in required_fields:
        if field not in request.json:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        arena_id = int(request.json["arena_id"])
        if arena_id not in arena_networks:
            return jsonify({"error": "Invalid Arena ID"}), 400
    except ValueError:
        return jsonify({"error": "Arena ID must be an integer"}), 400

    try:
        stats = {
            "life": int(request.json["life"]),
            "strength": int(request.json["strength"]),
            "armor": int(request.json["armor"]),
            "speed": int(request.json["speed"])
        }
        if sum(stats.values()) > 20:
            return jsonify({"error": "Total stats must not exceed 20"}), 400
        if any(value < 0 for value in stats.values()):
            return jsonify({"error": "Stats must be non-negative"}), 400
    except ValueError:
        return jsonify({"error": "All stats must be integers"}), 400

    character = CharacterProxy(
        cid=str(uuid.uuid4()),
        teamid=request.json["team_id"],
        life=stats["life"],
        strength=stats["strength"],
        armor=stats["armor"],
        speed=stats["speed"],
        arena_id=arena_id
    )
    current_app.engine.addPlayer(character, "my_ip")
    return jsonify(character.toDict()), 201

# PUT - mettre à jour un personnage - /character/<cid>
@routes_blueprint.route('/character/<string:cid>', methods=['PUT'])
def update_character(cid):
    
    arena = current_app.engine._arena
    characters = arena._playersList
    
    for character in characters:
        if character.isId(cid):
            character.setLife(request.json.get('life'))
            return jsonify(character.toDict()), 200
    return jsonify({"error": "Personnage non trouvé"}), 404

# DELETE - supprimer un personnage - /character/<cid>
@routes_blueprint.route('/character/<string:cid>', methods=['DELETE'])
def delete_character(cid):
    
    arena = current_app.engine._arena
    characters = arena._playersList
    for character in characters:
        if character.isId(cid):
            arena.removePlayer(character)
            return jsonify({"message": f"Personnage avec cid {cid} supprimé."}), 200
    return jsonify({"error": "Personnage non trouvé"}), 404

# POST - /character/action/switcharena/<character_id>/<arena_id>
@routes_blueprint.route('/character/action/switcharena/<string:character_id>/<string:arena_id>', methods=['POST'])
def switch_arena(character_id, arena_id):
    character_response = current_app.engine.getPlayerByName(character_id)
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

# POST - /character/action/<cid>/<action>
@routes_blueprint.route('/character/action/<string:cid>/<int:action_id>/<string:target_id>', methods=['POST'])
def action_arena(cid, action_id, target_id):
    
    arena = current_app.engine._arena
    dataCharacter = arena.getPlayerByName(id=cid)
    dataTarget = arena.getPlayerByName(id=target_id)
    
    if not dataCharacter:
        return jsonify({"error": f"Personnage avec cid {cid} non trouvé"}), 404
    if not dataTarget:
        return jsonify({"error": f"Cible avec cid {target_id} non trouvée"}), 404
    try:
        action = ACTION(action_id)  # Assure une correspondance directe avec un énumérateur
    except ValueError:
        return jsonify({"error": f"Action ID {action_id} non valide"}), 400

    # Appliquer l'action et vérifier si une cible est requise
    dataCharacter.setAction(action)
    if action in [ACTION.HIT, ACTION.BLOCK, ACTION.DODGE, ACTION.FLY]:
        dataCharacter.setTarget(dataTarget.getId())

    return jsonify({
        "message": f"Action '{actionToStr(action)}' définie pour {cid} sur cible {target_id}.",
        "character": dataCharacter.toDict()
    }), 200
    

def select_new_arena(arena_id):
    return arena_networks[arena_id]['arena_network']

def send_to_arena(url, character_data):
    host = url.split('//')[1]  # Extraire l'hôte de l'URL
    conn = http.client.HTTPConnection(host)
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(character_data)
    conn.request("POST", "/character/join/", body=json_data, headers=headers)
    return conn.getresponse()

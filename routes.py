# route.py

import json
import http.client
from Project.Engine.data import *
from Project.Engine.arena import *
from Project.Engine.character import *
from flask import current_app, jsonify, request, Blueprint
import uuid
import threading

# Créer un Blueprint pour enregistrer les routes dans app.py
routes_blueprint = Blueprint('routes', __name__)

arena_networks = {
    1: {"arena_network": "10.7.181.219:6969"},
    2: {"arena_network": "10.7.177.131:6969"}
}

# Initialiser un verrou global si nécessaire (optionnel)
route_lock = threading.Lock()

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

# GET - récupérer le personnage spécifique - /character/cid
@routes_blueprint.route('/character/<string:cid>', methods=['GET'])
def get_character():
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

# POST - /character/join/
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
    if not request.json:
        return jsonify({"error": "Request body is missing"}), 400

    arena = current_app.engine._arena
    characters = arena._playersList

    for character in characters:
        if character.isId(cid):
            new_life = request.json.get('life')
            if new_life is not None:
                try:
                    new_life = int(new_life)
                    if new_life < 0:
                        return jsonify({"error": "Life must be non-negative"}), 400
                    character.setLife(new_life)
                except ValueError:
                    return jsonify({"error": "Life must be an integer"}), 400
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

# PUT - /character/action/switcharena/<cid>/<action_id>/<arena_id>
@routes_blueprint.route('/character/action/switcharena/<string:cid>/<int:action_id>/<int:arena_id>', methods=['PUT'])
def switch_arena(cid, action_id, arena_id):
    
    arena = current_app.engine._arena
    dataCharacter = arena.getPlayerByName(id=cid)
    current_arena_id = dataCharacter.getArena()
    
    # current_arena_network = arena_networks.get(current_arena_id, {}).get("arena_network", "Unknown Network")

    if not dataCharacter:
        return jsonify({"error": f"Personnage avec cid {cid} non trouvé"}), 404
    
    try:
        action = ACTION(action_id)
    except ValueError:
        return jsonify({"error": f"Action ID {action_id} non valide"}), 400

    # Appliquer l'action et vérifier si une cible est requise
    dataCharacter.setAction(action)
    if action == ACTION.FLY:
        
        # Get the target network for the new arena
        new_arena_network = arena_networks.get(arena_id, {}).get("arena_network", None)
        
        if not new_arena_network:
            return jsonify({"error": f"Arène {arena_id} non trouvée"}), 404
        
        dataCharacter.setArena(arena_id)     
        
        try :
            send_to_arena(new_arena_network, dataCharacter.toDict()) 
        except Exception as e:
            return jsonify({"error": f"Impossible de se connecter à l'arène {arena_id} =>{e}"}), 500  
          
        # Store the character's data before removing them
        engine = current_app.engine
        if not hasattr(engine, 'left_players'):
            engine.left_players = []

        cid = dataCharacter.getId()
        team_id = dataCharacter._teamid
        gold = engine._goldBook.get(cid, 0)

        # Append the character's data to left_players
        engine.left_players.append({
            'cid': cid,
            'team_id': team_id,
            'gold': gold
        })

        delete_character(cid=cid)
        
    return jsonify({
        "message": f"Personnage '{cid}' a quitté l'arène {current_arena_id} pour aller sur l'arène {arena_id} (IP: {new_arena_network})",
        "character": dataCharacter.toDict()
    }), 200

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
    if dataTarget.isDead():
        return jsonify({"error": f"Cible avec cid {target_id} est déjà morte"}), 400

    try:
        action = ACTION(action_id)  # Assure une correspondance directe avec un énumérateur
    except ValueError:
        return jsonify({"error": f"Action ID {action_id} non valide"}), 400

    # Appliquer l'action et vérifier si une cible est requise
    current_app.engine.setActionTo(cid, action_id)
    if action in [ACTION.HIT, ACTION.BLOCK, ACTION.DODGE]:
        current_app.engine.setTargetTo(cid, target_id)

    return jsonify({
        "message": f"Action '{actionToStr(action)}' définie pour {cid} sur cible {target_id}.",
        "character": dataCharacter.toDict()
    }), 200

def send_to_arena(ip, character_data):
    
    """
    Sends character data to the target arena network.

    :param ip: The target network's IP address.
    :param character_data: The serialized character data to send.
    """
    
    url = f"http://{ip}/character/join/"  # Assuming the target network has this endpoint
    conn = http.client.HTTPConnection(ip)
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(character_data)

    # Send the POST request
    conn.request("POST", "/character/join/", body=json_data, headers=headers)
    response = conn.getresponse()

    # Handle response
    if response.status != 201:
        raise Exception(f"Failed to send character to {ip} => {response.status} {response.reason}")

    return response


@routes_blueprint.route('/ranking/individual/', methods=['GET'])
def get_individual_ranking():
    engine = current_app.engine
    players = engine._arena._playersList

   # Create a list for ranking data
    ranking_data = []

    # Include current players
    for char in players:
        ranking_data.append({
            "cid": char.getId(),
            "gold": engine._goldBook.get(char.getId(), 0),
            "team": char._teamid
        })

    # Include left players
    if hasattr(engine, 'left_players'):
        for player in engine.left_players:
            ranking_data.append({
                "cid": player['cid'],
                "gold": player['gold'],
                "team": player['team_id']
            })

    # Sort the combined ranking data by gold in descending order
    ranking_data.sort(key=lambda x: x['gold'], reverse=True)
    
    return jsonify({"ranking": ranking_data}), 200

@routes_blueprint.route('/ranking/team/', methods=['GET'])
def get_team_ranking():
    engine = current_app.engine
    players = engine._arena._playersList
    team_gold = {}

     # Accumulate gold for current players
    for char in players:
        team_id = char._teamid
        char_gold = engine._goldBook.get(char.getId(), 0)
        team_gold[team_id] = team_gold.get(team_id, 0) + char_gold

    # Accumulate gold for left players
    if hasattr(engine, 'left_players'):
        for player in engine.left_players:
            team_id = player['team_id']
            gold = player['gold']
            team_gold[team_id] = team_gold.get(team_id, 0) + gold

    # Sort teams by total gold
    ranking = sorted(team_gold.items(), key=lambda x: x[1], reverse=True)
    ranking_data = [{"team_id": team_id, "gold": gold} for team_id, gold in ranking]

    return jsonify({"ranking": ranking_data}), 200

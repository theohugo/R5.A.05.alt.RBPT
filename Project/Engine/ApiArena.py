from flask import Flask, jsonify, request, render_template, abort
import json
from character import *
from engine import *
from arena import *


app = Flask(__name__)

# Fonctions utilitaires
@app.route('/x') #ajoute de "x" pour éviter la casse
def index():
    return render_template('index.html')

@app.route('/arena1')
def arena():
    return render_template('arena1.html')

def load_data():
    with open('./gamesData.json') as json_file:
        return json.load(json_file)
    
def load_data_of_character(character_id):
    with open('./gamesData.json') as json_file:
        return json.load(json_file)["charactersList"][character_id]
    
def write_data(data):
    with open('./gamesData.json', 'w') as outfile:
        json.dump(data, outfile)

@app.route('/alldata/', methods=['GET'])
def get_all_datas():
    return jsonify(load_data())
# ---------------------------------- Routes prof ----------------------------------
#good
# - GET - /character/id/ - récupérer un personnages - cid
@app.route('/character/<character_id>', methods=['GET'])
def get_character(character_id):
    data = load_data()
    if character_id in data["charactersList"]:
        return jsonify(data["charactersList"][character_id])
    else:
        return jsonify({"error": "Personnage non trouvé"}), 404
#good
# - GET - /characters/ - récupéré les personnages d'une arène
@app.route('/characters/', methods=['GET'])
def get_characters():
    arena = Arena(engine._arena)
    return jsonify(arena._playersList)

#pas good
# # - POST - /character/join/ - ajouter un personnage à une arène - cid, teamid, life, strength, armor, speed
# @app.route('/character/join', methods=['POST'])
# def join_character():
#     if character_id in load_data_of_character("charactersList"):
#         return jsonify({"message": "Personnage déjà ajouté"}), 4
#     character = CharacterProxy(character_id, teamid, life, strength, armor, speed)
#     engine = Engine()
#     engine.addPlayer(character)
#     return jsonify({"message": "Personnage ajouté"}), 200

#pas good
#- POST - /character/<character_id>/action/<action_id>/target - ajouter une action à un personnage - cid, action, target
@app.route('/character/action/<character_id>/<action_id>/<target_id>', methods=['GET'])
def action_character(character_id,action_id,target_id):
    dataCharacters = load_data_of_character(character_id) #dict
    dataTarget = load_data_of_character(target_id)
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

# ---------------------------------- Données ----------------------------------

# Routes get de l'API
@app.route('/arenass/', methods=['GET'])
def get_all_arenas():
    return jsonify(load_data()["arenasList"])

@app.route('/characterss/', methods=['GET'])
def get_all_characters():
    return jsonify(load_data()["charactersList"])


@app.route('/arenas/<arena_id>', methods=['GET'])
def get_specific_arena(arena_id):
    data = load_data()["arenasList"]
    if arena_id in data:
        return jsonify(data[arena_id])
    else:
        return jsonify({"error": "Arène non trouvé"}), 404

@app.route('/characters/<character_id>', methods=['GET'])
def get_specific_character(character_id):
    data = load_data()["charactersList"]
    if character_id in data:
        return jsonify(data[character_id])
    else:
        return jsonify({"error": "Personnage non trouvé"}), 404

# Routes add de l'API
@app.route('/addData/', methods=['POST'])
def add_arena(arena_id):
    data = load_data()["arenasList"]
    if arena_id in data:
        abort(400, "Arène déjà existante")
    data[arena_id].append(arena_id)
    write_data(data)
    return jsonify(data), 200 

@app.route('/addData/characters/<character_id>', methods=['POST'])
def add_character(character_id):
    data = load_data()
    if character_id in data["characters"]:
        abort(400, "Personnage déjà existant")
    data["characters"][character_id] = request.json
    write_data(data)
    return jsonify(data), 200

#---------------------------------- Routes test ----------------------------------
@app.route('/updateCharacterData/', methods=['POST'])
def update_character_data():
    try:
        data = load_data()

        character_id = str(request.json.get('characterId'))
        new_life = int(request.json.get('newLife'))
        new_armor = int(request.json.get('newArmor'))

        if character_id in data["charactersList"]:
            data["charactersList"][character_id]['life'] = new_life
            data["charactersList"][character_id]['armor'] = new_armor
            if new_armor <= 0:
                data["charactersList"][character_id]['armor'] = 0
            if new_life <= 0:
                del data["charactersList"][character_id]
            write_data(data)
            return jsonify({'success': True, 'charactersList': data["charactersList"]})
        else:
            return jsonify({'success': False, 'error': f'Character not found: {character_id}'}), 404
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'error': 'Internal Server Error'}), 500



#----------------------------------------------------------------------------
@app.route('/addtoArena', methods=['POST'])
def add_character_to_arena_TEST():
    data = load_data()
    character_id = request.form['character']
    arena_id = request.form['arena']
    if arena_id not in data["arenasList"]:
        abort(404, "Arène non trouvée")
    # cherche si le personnage est dans une liste d'arène
    for arena in data["arenasList"]:
        if character_id in arena["characters"]:
            abort(400, "Personnage déjà dans une arène")
    data["arenasList"][arena_id]["characters"].append(character_id)
    write_data(data)
    return render_template('index.html'), 200

@app.route('/addData/arenas/<arena_id>/characters/<character_id>', methods=['POST'])
def add_character_to_arena(arena_id, character_id):
    data = load_data()
    if arena_id not in data["arenas"]:
        abort(404, "Arène non trouvée")
    if character_id not in data["characters"]:
        abort(404, "Personnage non trouvé")
    if character_id in data["arenas"][arena_id]["characters"]:
        abort(400, "Personnage déjà dans l'arène")
    if len(data["arenas"][arena_id]["characters"]) >= data["arenas"][arena_id]["capacity"]:
        abort(400, "Arène pleine")
    data["arenas"][arena_id]["characters"].append(character_id)
    write_data(data)
    return jsonify(data), 200

# Routes delete de l'API
@app.route('/deleteData/arenas/<arena_id>/characters/<character_id>', methods=['DELETE'])
def delete_character_from_arena(arena_id, character_id):
    data = load_data()
    if arena_id not in data["arenas"]:
        abort(404, "Arène non trouvée")
    if character_id not in data["characters"]:
        abort(404, "Personnage non trouvé")
    if character_id not in data["arenas"][arena_id]["characters"]:
        abort(400, "Personnage non dans l'arène")
    data["arenas"][arena_id]["characters"].remove(character_id)
    write_data(data)
    return jsonify(data), 200

#
# # Choisir une cible pour un personnage
# @app.route('/arenas/<arena_id>/characters/<character_id>/chooseTarget', methods=['PUT'])
# def choose_target(arena_id, character_id):
#     if arena_id not in arenas:
#         return jsonify({"error": "Arène non trouvée"}), 404

#     if character_id not in arenas[arena_id]["characters"]:
#         return jsonify({"error": "Personnage non trouvé dans l'arène"}), 404

#     target_id = request.json.get('target_id')
#     if target_id not in arenas[arena_id]["characters"]:
#         return jsonify({"error": "Cible non trouvée dans l'arène"}), 404

#     # Enregistrer la cible choisie pour le personnage
#     characters[character_id]["target"] = target_id
#     return jsonify({"message": "Cible choisie"}), 200

# # Choisir l'action d'un personnage
# @app.route('/arenas/<arena_id>/characters/<character_id>/chooseAction', methods=['PUT'])
# def choose_action(arena_id, character_id):
#     if arena_id not in arenas:
#         return jsonify({"error": "Arène non trouvée"}), 404

#     if character_id not in arenas[arena_id]["characters"]:
#         return jsonify({"error": "Personnage non trouvé dans l'arène"}), 404

#     action = request.json.get('action')
#     if action not in ["hit", "block", "dodge", "fly"]:
#         return jsonify({"error": "Action invalide"}), 400

#     # Enregistrer l'action choisie pour le personnage
#     characters[character_id]["action"] = action
#     return jsonify({"message": "Action choisie"}), 200

# Démarrer le serveur
if __name__ == '__main__':
    engine = Engine()
    app.run(debug=True)
    engine.run()

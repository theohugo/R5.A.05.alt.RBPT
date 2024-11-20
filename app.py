from flask import Flask, jsonify, request

app = Flask(__name__)

arena_networks = {
    1, 2
}

characters = [
    {
        "cid": 1,
        "team_id": 1,
        "arena_id": 2,
        "life": 5,
        "strengh": 3,
        "armor": 3,
        "speed": 2
    },
    {
        "cid": 2,
        "team_id": 2,
        "arena_id": 2,
        "life": 8,
        "strengh": 23,
        "armor": 34,
        "speed": 25
    },
    {
        "cid": 1,
        "team_id": 1,
        "arena_id": 2,
        "life": 80,
        "strengh": 30,
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
    # returning a dict or list equals to use jsonify()
    return {'message': 'Hello!'}


# GET - récupérer les personnages d'une arène - /characters/
@app.route('/characters/', methods=['GET'])
def get_characters():
    return jsonify({"characters": characters})

# GET - récupérer les résultats des matchs /status/ - numéro de tour
@app.route('/status/', methods=['GET'])
def get_matches():
    return jsonify({"matches": matches})

# GET - récupérer un personnage - /character/cid
@app.route('/character/<int:cid>', methods=['GET'])
def get_character(cid):
    character = next((character for character in characters if character["cid"] == cid), None)
    if character is None:
        return jsonify({"error": "character not found"}), 404
    return jsonify(character)

# POST - ajouter un personnage à une arène - /character/join/ - cid, teamid, life, strength, armor, speed
@app.route('/character/join/', methods=['POST'])
def create_character():

    if ( not request.json or "arena_id" not in request.json ):
        return jsonify({"error": "Bad Request"}), 400
    
    arena_id = request.json["arena_id"]
    if ( arena_id not in arena_networks ):
        return jsonify({"error": "Invalid Arena ID"}), 400

    new_character = {
        "cid": characters[-1]["cid"] + 1 if characters else 1,
        "team_id": request.json["team_id"],
        "arena_id": request.json["arena_id"],
        "life": request.json["life"],
        "strength": request.json["strength"],
        "armor": request.json["armor"],
        "speed": request.json["speed"]
    }
    
    characters.append(new_character)
    return jsonify(new_character), 201

# PUT to update a character
@app.route('/character/<int:cid>', methods=['PUT'])
def update_character(cid):
    
    character = next((character for character in characters if character["cid"] == cid), None)
    
    if character is None:
        return jsonify({"error": "character not found"}), 404
    if not request.json:
        return jsonify({"error": "Bad Request"}), 400

    character["arena_id"] = request.json.get("arena_id", character["arena_id"])

    return jsonify(character)

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

if __name__ == '__main__':
    app.run(debug=True)

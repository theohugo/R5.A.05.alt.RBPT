import unittest
import requests
import random

class TestEngineRealAPI(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000"
    
    def setUp(self):
        """Initialisation pour chaque test."""
        self.players = []  
        self.rounds = 3

    def create_player(self, player_data):
        """Créer un joueur via l'API et retourner son ID."""
        response = requests.post(f"{self.BASE_URL}/character/join/", json=player_data)
        self.assertEqual(response.status_code, 201, f"Player creation failed: {response.json()}")
        return response.json()['cid']

    def perform_action(self, actor_id, action_id, target_id):
        """Effectuer une action pour un joueur."""
        response = requests.post(
            f"{self.BASE_URL}/character/action/{actor_id}/{action_id}/{target_id}"
        )
        self.assertEqual(response.status_code, 200, f"Action failed: {response.json()}")
        return response.json()

    def get_all_players(self):
        """Récupérer l'état actuel de tous les joueurs."""
        response = requests.get(f"{self.BASE_URL}/characters/")
        self.assertEqual(response.status_code, 200, f"Failed to fetch players: {response.json()}")
        return response.json()['characters']

    def test_turns(self):
        """Ajouter plusieurs joueurs et effectuer des actions sur plusieurs tours."""
        # Étape 1 : Ajouter des joueurs
        player_1_data = {
            "team_id": 1,
            "arena_id": 2,
            "life": 8,
            "strength": 5,
            "armor": 3,
            "speed": 4
        }
        player_2_data = {
            "team_id": 2,
            "arena_id": 2,
            "life": 6,
            "strength": 6,
            "armor": 5,
            "speed": 3
        }
        player_3_data = {
            "team_id": 3,
            "arena_id": 2,
            "life": 8,
            "strength": 4,
            "armor": 6,
            "speed": 2
        }

        # Créer les joueurs
        player_1_id = self.create_player(player_1_data)
        player_2_id = self.create_player(player_2_data)
        player_3_id = self.create_player(player_3_data)

        self.players = [player_1_id, player_2_id, player_3_id]

        # Étape 2 : Effectuer plusieurs rounds
        for round_num in range(self.rounds):
            print(f"--- Round {round_num + 1} ---")
            action_1 = self.perform_action(player_1_id, 0, player_2_id)  # Player 1 attaque Player 2
            print(f"Player 1 hits Player 2: {action_1['message']}")

            action_2 = self.perform_action(player_2_id, 1, player_1_id)  # Player 2 bloque
            print(f"Player 2 blocks Player 1: {action_2['message']}")

            action_3 = self.perform_action(player_3_id, 0, player_1_id)  # Player 3 attaque Player 1
            print(f"Player 3 hits Player 1: {action_3['message']}")

            current_state = self.get_all_players()
            for char in current_state:
                print(f"Player {char['cid']} - Life: {char['life']}")
                
            print(f'--- End of Round {round_num + 1 } ---')

        # Étape 3 : Vérification finale
        final_state = self.get_all_players()
        print("--- Final State ---")
        for char in final_state:
            print(f"Player {char['cid']} - Life: {char['life']}")


if __name__ == '__main__':
    unittest.main()

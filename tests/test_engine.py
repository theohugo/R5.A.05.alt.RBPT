import unittest
import requests
import random
import time

class TestEngineRealAPI(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000"
    
    def setUp(self):
        """Initialisation pour chaque test."""
        self.players = []

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

    def update_active_players(self):
        """Mettre à jour la liste des joueurs actifs (ceux qui sont encore en vie)."""
        current_state = self.get_all_players()
        self.players = [char['cid'] for char in current_state if not char['dead']]

    def get_teams(self):
        """Retourner les équipes actives."""
        current_state = self.get_all_players()
        teams = set(char['teamid'] for char in current_state if not char['dead'])
        return teams

    def display_individual_ranking(self, ranking_data):
        """Affichage du classement individuel."""
        print("\n=== Classement Individuel ===")
        top_3_individuals = ranking_data[:3]
        others_individuals = ranking_data[3:]

        print("\n--- Top 3 Joueurs ---")
        for rank, player in enumerate(top_3_individuals, start=1):
            print(f"#{rank}: Joueur ID: {player['cid']}, Or: {player['gold']}, Équipe: {player['team']}")

        if others_individuals:
            print("\n--- Autres Joueurs ---")
            for rank, player in enumerate(others_individuals, start=4):
                print(f"#{rank}: Joueur ID: {player['cid']}, Or: {player['gold']}, Équipe: {player['team']}")

    def display_team_ranking(self, ranking_data):
        """Affichage du classement par équipe."""
        print("\n=== Classement par Équipe ===")
        top_3_teams = ranking_data[:3]
        others_teams = ranking_data[3:]

        print("\n--- Top 3 Équipes ---")
        for rank, team in enumerate(top_3_teams, start=1):
            print(f"#{rank}: Équipe ID: {team['team_id']}, Or Total: {team['gold']}")

        if others_teams:
            print("\n--- Autres Équipes ---")
            for rank, team in enumerate(others_teams, start=4):
                print(f"#{rank}: Équipe ID: {team['team_id']}, Or Total: {team['gold']}")

    def test_until_last_team_standing(self):
        """Continuer jusqu'à ce qu'il ne reste plus qu'une équipe."""
        teams = 5
        players_per_team = 3

        # Étape 1 : Ajouter les joueurs
        for team_id in range(1, teams + 1):
            for player_index in range(players_per_team):
                valid_stats = False
                while not valid_stats:
                    life = random.randint(5, 10)
                    strength = random.randint(3, 7)
                    armor = random.randint(2, 5)
                    speed = random.randint(1, 5)
                    stats_sum = life + strength + armor + speed
                    if stats_sum <= 20:
                        valid_stats = True

                player_data = {
                    "team_id": team_id,
                    "arena_id": 2,
                    "life": life,
                    "strength": strength,
                    "armor": armor,
                    "speed": speed
                }
                player_id = self.create_player(player_data)
                self.players.append(player_id)
                time.sleep(0.5)

        # Étape 2 : Continuer jusqu'à ce qu'il ne reste plus qu'une équipe
        while len(self.get_teams()) > 1:
            self.update_active_players()

            if len(self.players) < 2:
                break

            for player_id in self.players:
                possible_targets = [pid for pid in self.players if pid != player_id]
                if not possible_targets:
                    continue

                target_id = random.choice(possible_targets)
                action_id = random.choice([0, 1, 2, 3])

                try:
                    self.perform_action(player_id, action_id, target_id)
                except AssertionError as e:
                    print(f"Action failed for Player {player_id} on target {target_id}: {str(e)}")

                time.sleep(0.2)

        # Étape 3 : Récupérer le classement individuel et par équipe
        individual_ranking = requests.get(f"{self.BASE_URL}/ranking/individual/")
        self.assertEqual(individual_ranking.status_code, 200)
        individual_ranking_data = individual_ranking.json()["ranking"]

        team_ranking = requests.get(f"{self.BASE_URL}/ranking/team/")
        self.assertEqual(team_ranking.status_code, 200)
        team_ranking_data = team_ranking.json()["ranking"]

        # Afficher les classements avec les fonctions
        self.display_individual_ranking(individual_ranking_data)
        self.display_team_ranking(team_ranking_data)

if __name__ == '__main__':
    unittest.main()

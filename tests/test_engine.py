import unittest
import requests
import random
import time

class TestEngineRealAPI(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000"
    
    def setUp(self):
        """Initialisation pour chaque test."""
        self.players = []
        self.round_number = 0  # Pour suivre le nombre de rounds

    # Fonctions Utilitaires

    def create_player(self, player_data):
        """Créer un joueur via l'API et retourner son ID."""
        response = requests.post(f"{self.BASE_URL}/character/join/", json=player_data)
        self.assertEqual(response.status_code, 201, f"Player creation failed: {response.json()}")
        player_id = response.json()['cid']
        print(f"[INFO] Joueur créé : ID = {player_id}, Données = {player_data}")
        return player_id

    def perform_action(self, actor_id, action_id, target_id):
        """Effectuer une action pour un joueur."""
        response = requests.post(
            f"{self.BASE_URL}/character/action/{actor_id}/{action_id}/{target_id}"
        )
        if response.status_code != 200:
            error_message = response.json().get('error', 'Unknown error')
            print(f"[ERROR] Action échouée pour Joueur {actor_id} sur Cible {target_id} avec Action {action_id}: {error_message}")
        else:
            print(f"[ACTION] Joueur {actor_id} a effectué l'action {action_id} sur la cible {target_id} avec succès.")
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
        print(f"[INFO] Joueurs encore en vie : {self.players}")

    def get_teams(self):
        """Retourner les équipes actives."""
        current_state = self.get_all_players()
        teams = set(char['team_id'] for char in current_state if not char['dead'])
        return teams

    def organize_teams(self, players):
        """Organiser les joueurs par équipe."""
        teams = {}
        for player in players:
            if player['team_id'] not in teams:
                teams[player['team_id']] = []
            teams[player['team_id']].append(player)
        return teams

    # Affichages

    def format_life(self, life):
        """Formater la vie avec deux chiffres après la virgule."""
        return f"{life:.2f}"

    def display_round_status(self):
        """Affichage ASCII de l'état des équipes et joueurs après chaque round."""
        players = self.get_all_players()
        teams = self.organize_teams(players)

        team_keys = list(teams.keys())
        grouped_teams = [team_keys[i:i + 5] for i in range(0, len(team_keys), 5)]

        print("\n=== État des Joueurs à la Fin du Round ===")

        for group in grouped_teams:
            # Impression des noms des équipes
            team_headers = ""
            for team_id in group:
                team_headers += f"Équipe {team_id}".center(25) + " "
            print(team_headers)

            # Impression des séparateurs
            separators = "+-----------+---------------+" * len(group)
            print(separators)

            # Impression des détails des joueurs
            max_players = max(len(teams[team]) for team in group)
            for i in range(max_players):
                row = ""
                for team_id in group:
                    if i < len(teams[team_id]):
                        player = teams[team_id][i]
                        life = self.format_life(player['life']) if not player['dead'] else "MORT"
                        row += f"| {player['cid'][:8]} | Vie: {life}".ljust(25) + " "
                    else:
                        row += " " * 25 + " "
                print(row)

            # Impression des séparateurs de fin
            print(separators)

    def display_end_game_status(self):
        """Affichage ASCII de l'état final des joueurs et équipes."""
        players = self.get_all_players()
        teams = self.organize_teams(players)

        team_keys = list(teams.keys())
        grouped_teams = [team_keys[i:i + 5] for i in range(0, len(team_keys), 5)]

        print("\n=== État Final des Joueurs ===")

        for group in grouped_teams:
            # Impression des noms des équipes
            team_headers = ""
            for team_id in group:
                team_headers += f"Équipe {team_id}".center(25) + " "
            print(team_headers)

            # Impression des séparateurs
            separators = "+-----------+---------------+" * len(group)
            print(separators)

            # Impression des détails des joueurs
            max_players = max(len(teams[team]) for team in group)
            for i in range(max_players):
                row = ""
                for team_id in group:
                    if i < len(teams[team_id]):
                        player = teams[team_id][i]
                        life = self.format_life(player['life']) if not player['dead'] else "MORT"
                        row += f"| {player['cid'][:8]} | Vie: {life}".ljust(25) + " "
                    else:
                        row += " " * 25 + " "
                print(row)

            # Impression des séparateurs de fin
            print(separators)

    def display_individual_ranking(self, ranking_data):
        """Affichage du classement individuel."""
        print("\n=== Classement Individuel ===")
        top_3_individuals = ranking_data[:3]
        others_individuals = ranking_data[3:]

        print("\n--- Top 3 Joueurs ---")
        for rank, player in enumerate(top_3_individuals, start=1):
            print(f"#{rank}: Joueur ID: {player['cid']}, Or: {player['gold']:.2f}, Équipe: {player['team']}")

        if others_individuals:
            print("\n--- Autres Joueurs ---")
            for rank, player in enumerate(others_individuals, start=4):
                print(f"#{rank}: Joueur ID: {player['cid']}, Or: {player['gold']:.2f}, Équipe: {player['team']}")

    def display_team_ranking(self, ranking_data):
        """Affichage du classement par équipe."""
        print("\n=== Classement par Équipe ===")
        top_3_teams = ranking_data[:3]
        others_teams = ranking_data[3:]

        print("\n--- Top 3 Équipes ---")
        for rank, team in enumerate(top_3_teams, start=1):
            print(f"#{rank}: Équipe ID: {team['team_id']}, Or Total: {team['gold']:.2f}")

        if others_teams:
            print("\n--- Autres Équipes ---")
            for rank, team in enumerate(others_teams, start=4):
                print(f"#{rank}: Équipe ID: {team['team_id']}, Or Total: {team['gold']:.2f}")

    def verify_all_players_created(self):
        """Vérifie que tous les joueurs créés sont bien présents dans l'API."""
        retrieved_players = self.get_all_players()
        retrieved_player_ids = {player['cid'] for player in retrieved_players}
        created_player_ids = set(self.players)
        missing_players = created_player_ids - retrieved_player_ids
        self.assertTrue(
            not missing_players,
            f"Les joueurs suivants n'ont pas été retrouvés lors de la récupération : {missing_players}"
        )
        print(f"[INFO] Tous les joueurs créés ont été retrouvés dans l'API.")

    # Test Principal

    def test_until_last_team_standing(self):
        """Continuer jusqu'à ce qu'il ne reste plus qu'une équipe."""
        # Étape 1 : Ajouter les players
        teams = 3
        players_per_team = 2
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
        self.round_number = 0

        # Étape 1.1 : Vérifier que tous les joueurs créés sont bien présents
        self.verify_all_players_created()

        # Étape 2 : Continuer jusqu'à ce qu'il ne reste plus qu'une équipe
        while len(self.get_teams()) > 1:
            self.round_number += 1
            print(f"\n=== Début du Round {self.round_number} ===")
            
            # Ne pas mettre à jour la liste des joueurs encore en vie avant chaque action,
            # car ils doivent agir sans connaître l'état à jour des autres.
            initial_players = self.players[:]
            possible_targets = [pid for pid in initial_players if pid != player_id]
            for player_id in initial_players:
                target_id = random.choice(possible_targets)
                action_id = random.choice([0, 1, 2])

                try:
                    self.perform_action(player_id, action_id, target_id)
                except AssertionError as e:
                    print(f"[ERROR] Action échouée pour Joueur {player_id} sur Cible {target_id}: {str(e)}")

            # Mettre à jour la liste des joueurs après le round
            self.update_active_players()

            # Afficher l'état des joueurs à la fin de chaque round
            self.display_round_status()
            print(f"=== Fin du Round {self.round_number} ===")
            time.sleep(1)

        
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

        # Afficher l'état final des joueurs
        self.display_end_game_status()

        # Étape 4 : Vérifier une nouvelle fois que tous les joueurs créés sont toujours présents
        self.verify_all_players_created()

if __name__ == '__main__':
    unittest.main()

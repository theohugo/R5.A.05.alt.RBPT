import requests
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import random

# Mapping centralisé des URLs des arènes à leurs arena_id
ARENA_MAPPING = {
    "http://10.109.150.192:6969": 1,
    "http://10.109.150.75:6969": 2,
    # Ajouter d'autres mappings si nécessaire
}

# Mapping inverse pour retrouver l'URL à partir de l'arena_id
REVERSE_ARENA_MAPPING = {v: k for k, v in ARENA_MAPPING.items()}

class AgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent GUI")
        self.create_widgets()
        self.agents = []
        self.turn_logs = []
        self.turn_number = 0
        self.running = True

        # Générer un team_id unique pour tous les agents
        self.team_id = self.get_unique_team_id()

        # Lancer la mise à jour des données en arrière-plan
        threading.Thread(target=self.update_loop, daemon=True).start()

    def create_widgets(self):
        # Cadre principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Section pour les agents
        agents_frame = ttk.LabelFrame(main_frame, text="Agents")
        agents_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tableau pour afficher les agents
        columns = ("Bot Name", "Life", "Action", "Reasoning", "Arena ID")
        self.tree = ttk.Treeview(agents_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor='center')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Section pour les logs
        logs_frame = ttk.LabelFrame(main_frame, text="Logs des Tours")
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Zone de texte pour les logs
        self.logs_text = tk.Text(logs_frame, height=10, state='disabled')
        self.logs_text.pack(fill=tk.BOTH, expand=True)

        # Cadre pour les contrôles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # Sélection du nombre de membres de l'équipe
        ttk.Label(controls_frame, text="Nombre de membres de l'équipe:").pack(side=tk.LEFT, padx=5)
        self.num_agents_var = tk.IntVar(value=3)
        num_agents_spinbox = ttk.Spinbox(controls_frame, from_=1, to=10, textvariable=self.num_agents_var, width=5)
        num_agents_spinbox.pack(side=tk.LEFT, padx=5)

        # Bouton pour démarrer/arrêter
        self.start_button = ttk.Button(controls_frame, text="Démarrer les Agents", command=self.start_agents)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(controls_frame, text="Arrêter les Agents", command=self.stop_agents)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.config(state=tk.DISABLED)

        # Section pour les classements
        rankings_frame = ttk.Frame(main_frame)
        rankings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tableau pour le classement individuel
        individual_rank_frame = ttk.LabelFrame(rankings_frame, text="Classement Individuel")
        individual_rank_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.individual_tree = ttk.Treeview(individual_rank_frame, columns=("CID", "Gold", "Team"), show='headings')
        for col in ("CID", "Gold", "Team"):
            self.individual_tree.heading(col, text=col)
            self.individual_tree.column(col, width=100, anchor='center')
        self.individual_tree.pack(fill=tk.BOTH, expand=True)

        # Tableau pour le classement par équipe
        team_rank_frame = ttk.LabelFrame(rankings_frame, text="Classement par Équipe")
        team_rank_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.team_tree = ttk.Treeview(team_rank_frame, columns=("Team ID", "Gold"), show='headings')
        for col in ("Team ID", "Gold"):
            self.team_tree.heading(col, text=col)
            self.team_tree.column(col, width=100, anchor='center')
        self.team_tree.pack(fill=tk.BOTH, expand=True)

    def start_agents(self):
        # Désactiver le bouton de démarrage
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Récupérer le nombre de membres de l'équipe
        num_agents = self.num_agents_var.get()
        if num_agents < 1:
            messagebox.showerror("Erreur", "Le nombre de membres de l'équipe doit être au moins 1.")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            return

        # Créer les agents en assignant une arène initiale
        self.agents = self.create_agents(num_agents)

        # Réinitialiser les logs et le numéro de tour
        self.turn_logs = []
        self.turn_number = 0

        # Lancer le thread de jeu
        threading.Thread(target=self.game_loop, daemon=True).start()

    def stop_agents(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def create_agents(self, num_agents):
        agents = []
        roles = ["Attacker", "Defender", "Support"]
        num_arenas = len(ARENA_MAPPING)
        for i in range(num_agents):
            role = random.choice(roles)
            bot_name = f"{role}_{i+1}"
            # Assigner une arène initiale en utilisant une répartition circulaire
            arena_index = i % num_arenas
            arena_url = list(ARENA_MAPPING.keys())[arena_index]
            arena_id = ARENA_MAPPING[arena_url]
            agent = BotAgent(bot_name, self.team_id, arena_url, arena_id, num_agents, role)
            agents.append(agent)
        return agents

    def get_unique_team_id(self):
        try:
            # Utiliser la première arène pour obtenir les characters et déterminer le team_id
            response = requests.get(f"{list(ARENA_MAPPING.keys())[0]}/characters/")
            response.raise_for_status()
            characters = response.json()['characters']
            existing_team_ids = set(char.get('teamid', char.get('team_id')) for char in characters)
            new_team_id = 1
            while new_team_id in existing_team_ids:
                new_team_id += 1
            return new_team_id
        except requests.exceptions.RequestException:
            return random.randint(1000, 9999)

    def update_agents_table(self):
        # Effacer les données existantes
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Insérer les nouvelles données
        for agent in self.agents:
            self.tree.insert("", "end", values=(
                agent.bot_name,
                agent.life,
                agent.action,
                agent.reasoning,
                agent.arena_id
            ))

    def update_logs(self):
        self.logs_text.config(state='normal')
        self.logs_text.delete(1.0, tk.END)
        for turn_log in self.turn_logs[-5:]:
            self.logs_text.insert(tk.END, f"=== Tour {turn_log['turn']} ===\n")
            for action in turn_log["actions"]:
                log_line = f"{action['bot_name']} (Vie: {action['life']}): {action['action']} - {action['reasoning']}\n"
                self.logs_text.insert(tk.END, log_line)
            self.logs_text.insert(tk.END, "\n")
        self.logs_text.config(state='disabled')

    def update_rankings(self):
        try:
            # Récupérer les classements individuels depuis toutes les arènes
            ranking_individual = []
            for arena_url in ARENA_MAPPING.keys():
                response_individual = requests.get(f"{arena_url}/ranking/individual/")
                response_individual.raise_for_status()
                ranking_individual.extend(response_individual.json()['ranking'])

            # Mettre à jour le tableau individuel
            for row in self.individual_tree.get_children():
                self.individual_tree.delete(row)
            for player in ranking_individual:
                self.individual_tree.insert("", "end", values=(
                    player['cid'][:8],  # Afficher les 8 premiers caractères du CID
                    player['gold'],
                    player['team']
                ))

            # Récupérer les classements par équipe depuis toutes les arènes
            ranking_team = []
            for arena_url in ARENA_MAPPING.keys():
                response_team = requests.get(f"{arena_url}/ranking/team/")
                response_team.raise_for_status()
                ranking_team.extend(response_team.json()['ranking'])

            # Mettre à jour le tableau par équipe
            for row in self.team_tree.get_children():
                self.team_tree.delete(row)
            # Agréger les golds par équipe
            team_gold = {}
            for team in ranking_team:
                team_id = team['team_id']
                gold = team['gold']
                team_gold[team_id] = team_gold.get(team_id, 0) + gold
            # Trier les équipes par gold décroissant
            sorted_teams = sorted(team_gold.items(), key=lambda x: x[1], reverse=True)
            for team_id, gold in sorted_teams:
                self.team_tree.insert("", "end", values=(
                    team_id,
                    gold
                ))
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Échec de la récupération des classements: {e}")

    def update_loop(self):
        while True:
            if self.agents:
                self.update_agents_table()
                self.update_rankings()
            time.sleep(5)  # Mettre à jour toutes les 5 secondes

    def game_loop(self):
        self.running = True
        while self.running:
            self.turn_number += 1
            turn_log = {"turn": self.turn_number, "actions": []}
            print(f"\n=== TOUR {self.turn_number} ===")
            # Obtenir l'état du jeu pour chaque arène
            all_game_states = {}
            for arena_url in ARENA_MAPPING.keys():
                game_state = self.get_game_state(arena_url)
                all_game_states[arena_url] = game_state

            for agent in self.agents:
                if not self.running:
                    break
                agent.is_alive(all_game_states.get(agent.arena_url, []))
                if not agent.alive:
                    continue
                action_id, target_id = agent.decide_action(all_game_states, self.agents, self.turn_number)
                if action_id is not None and target_id is not None:
                    agent.perform_action(action_id, target_id)
                    # Attendre 2 secondes entre chaque envoi d'action
                    time.sleep(2)
                turn_log["actions"].append({
                    "bot_name": agent.bot_name,
                    "life": agent.life,
                    "action": agent.action,
                    "reasoning": agent.reasoning
                })
            self.turn_logs.append(turn_log)
            self.update_logs()
            time.sleep(1)

    def get_game_state(self, arena_url):
        try:
            response = requests.get(f"{arena_url}/characters/")
            response.raise_for_status()
            return response.json()['characters']
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Impossible de récupérer l'état du jeu depuis {arena_url}:\n{e}")
            return []

    def update_team_strategy(self, game_state, agent):
        # Cibler les ennemis en optimisant les dégâts
        agents_team_id = agent.team_id
        enemies = [char for char in game_state if char.get('teamid') != agents_team_id and not char.get('dead')]
        if not enemies:
            return {}
        # Trier les ennemis par vie effective croissante
        enemies.sort(key=lambda x: x.get('life', 0) + x.get('armor', 0))
        # Attribuer les cibles aux agents en fonction de la force
        targets = {}
        enemy_index = 0
        for agent in self.agents:
            if agent.alive:
                # Si tous les ennemis ont été attribués, recommencer depuis le premier
                if enemy_index >= len(enemies):
                    enemy_index = 0
                target_enemy = enemies[enemy_index]
                targets[agent.cid] = target_enemy['cid']
                enemy_index += 1
        return targets

class BotAgent:
    def __init__(self, bot_name, team_id, arena_url, arena_id, num_agents, role):
        self.bot_name = bot_name
        self.cid = None
        self.team_id = team_id  # Ajout de team_id
        self.arena_url = arena_url
        self.arena_id = arena_id
        self.num_agents = num_agents
        self.role = role
        self.life = 0
        self.action = "Attente"
        self.reasoning = ""
        self.alive = True
        self.strength = 0
        self.speed = 0
        self.armor = 0
        self.last_action = None  # Track the last action performed
        self.create_agent()
        self.defense_counter = 0  # Compteur pour éviter les boucles de défense

    def create_agent(self):
        stats = self.allocate_stats()
        data = {
            "team_id": self.team_id,  # Utiliser team_id correctement
            "arena_id": self.arena_id,
            "life": stats['life'],
            "strength": stats['strength'],
            "armor": stats['armor'],
            "speed": stats['speed']
        }
        try:
            print(f"[DEBUG] Envoyer les données à /character/join/ pour {self.bot_name}: {data}")
            response = requests.post(f"{self.arena_url}/character/join/", json=data)
            response.raise_for_status()
            response_data = response.json()
            self.cid = response_data.get('cid')
            self.life = stats['life']
            self.strength = stats['strength']
            self.armor = stats['armor']
            self.speed = stats['speed']
            print(f"[INFO] {self.bot_name} créé : ID = {self.cid}, Données = {data}, Arène = {self.arena_id}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] {self.bot_name}: Échec de la création du joueur:\n{e}")

    def allocate_stats(self):
        # Ajuster les points de statistiques totaux par agent en fonction du nombre de membres de l'équipe
        total_stat_points = max(20, int(60 / self.num_agents))
        # Commencer avec 1 point dans chaque statistique
        stats = {'life': 1, 'strength': 1, 'armor': 1, 'speed': 1}
        points_left = total_stat_points - 4  # Soustraire les 4 points déjà assignés

        # Définir les priorités des statistiques en fonction du rôle
        stat_priority = {
            'Attacker': ['strength', 'life', 'speed', 'armor'],
            'Defender': ['life', 'armor', 'strength', 'speed'],
            'Support': ['speed', 'life', 'armor', 'strength']
        }
        priority = stat_priority.get(self.role, ['life', 'strength', 'armor', 'speed'])

        # Allouer les points restants en fonction des priorités avec une certaine randomisation
        while points_left > 0:
            for stat in priority:
                if points_left <= 0:
                    break
                # Introduire une probabilité d'allocation aléatoire
                if random.random() > 0.2:  # 80% de chance d'ajouter un point à la priorité
                    stats[stat] += 1
                    points_left -= 1
        return stats

    def get_game_state(self, arena_url):
        try:
            response = requests.get(f"{arena_url}/characters/")
            response.raise_for_status()
            return response.json()['characters']
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] {self.bot_name}: Impossible de récupérer l'état du jeu depuis {arena_url}:\n{e}")
            return []

    def is_alive(self, game_state):
        my_character = next((char for char in game_state if char.get('cid') == self.cid), None)
        if my_character and not my_character.get('dead', False):
            self.alive = True
            self.life = my_character.get('life', 0)
            return True
        else:
            self.alive = False
            self.action = "Mort"
            self.reasoning = "Je suis mort."
            return False

    def decide_action(self, all_game_states, agents, turn_number):
        if not self.alive:
            return None, None
        game_state = all_game_states.get(self.arena_url, [])
        my_character = next((char for char in game_state if char.get('cid') == self.cid), None)
        if not my_character:
            self.alive = False
            self.action = "Mort"
            self.reasoning = "Personnage introuvable."
            return None, None
        self.life = my_character.get('life', 0)
        my_life = self.life
        my_team = my_character.get('teamid') or my_character.get('team_id')  # Assurer l'accès à teamid
        enemies = [char for char in game_state if char.get('teamid') != my_team and not char.get('dead', False)]
        allies = [char for char in game_state if char.get('teamid') == my_team and not char.get('dead', False)]
        if not enemies:
            self.action = "Attente"
            self.reasoning = "Aucun ennemi restant."
            return None, None

        # Vérifier si les ennemis attaquent
        enemy_actions = self.get_enemy_actions(all_game_states, my_team)
        under_attack = any(action in ['HIT', 'Action 0'] for action in enemy_actions.values())

        # Estimer si l'agent sera attaqué avant de pouvoir agir
        my_speed = my_character.get('speed', 0)
        enemy_speeds = [enemy.get('speed', 0) for enemy in enemies]
        faster_enemies = [speed for speed in enemy_speeds if speed >= my_speed]

        # Décision basée sur la vitesse relative et le tour actuel
        if (faster_enemies and turn_number == 1) or (my_life < 5):
            # Si des ennemis sont plus rapides au premier tour, ou si la vie est basse
            if self.defense_counter >= 2 or not under_attack:
                # Si on s'est déjà défendu plusieurs fois ou qu'on n'est pas attaqué, attaquer
                action_id = 0  # HIT
                self.action = "Attaque"
                self.reasoning = f"Je décide d'attaquer pour éviter la boucle."
                self.defense_counter = 0
                self.last_action = "ATTACK"  # Track last action
            else:
                # Prevent defending if last action was defend
                if self.last_action != "DEFEND":
                    action_id = random.choice([1, 2])  # BLOCK ou DODGE
                    self.action = "Se Défend"
                    self.reasoning = f"Des ennemis plus rapides pourraient m'attaquer. Je me défends."
                    self.defense_counter += 1
                    self.last_action = "DEFEND"  # Track last action
                else:
                    # Si la dernière action était défendre, attaquer à la place
                    action_id = 0  # HIT
                    self.action = "Attaque"
                    self.reasoning = f"J'ai déjà défendu récemment. J'attaque la cible assignée."
                    self.defense_counter = 0
                    self.last_action = "ATTACK"  # Track last action
        else:
            self.defense_counter = 0
            if self.role == "Attacker":
                action_id = 0  # HIT
                self.action = "Attaque"
                self.reasoning = f"Attaquant. J'attaque la cible assignée."
                self.last_action = "ATTACK"  # Track last action
            elif self.role == "Defender":
                if any(ally.get('life', 0) < 5 for ally in allies if ally.get('cid') != self.cid):
                    ally_in_need = min(
                        [ally for ally in allies if ally.get('cid') != self.cid and ally.get('life', 0) < 5],
                        key=lambda x: x.get('life', 0),
                        default=None
                    )
                    if ally_in_need:
                        # Prevent defending if last action was defend
                        if self.last_action != "DEFEND":
                            action_id = random.choice([1, 2])  # BLOCK ou DODGE
                            target_id = ally_in_need.get('cid')
                            self.action = "Protège"
                            self.reasoning = f"Défenseur. Je protège l'allié {target_id[:4]}."
                            self.last_action = "DEFEND"  # Track last action
                            return action_id, target_id
                action_id = 0  # HIT
                self.action = "Attaque"
                self.reasoning = f"Aucun allié en danger. J'attaque la cible assignée."
                self.last_action = "ATTACK"  # Track last action
            elif self.role == "Support":
                # Le support ne peut plus soigner, il attaquera ou se défendra
                # Exemple : Prioriser la défense si sous attaque, sinon attaquer
                if under_attack:
                    # Prevent defending if last action was defend
                    if self.last_action != "DEFEND":
                        action_id = random.choice([1, 2])  # BLOCK ou DODGE
                        self.action = "Se Défend"
                        self.reasoning = f"Support sous attaque. Je me défends."
                        self.last_action = "DEFEND"  # Track last action
                    else:
                        # Si la dernière action était défendre, attaquer à la place
                        action_id = 0  # HIT
                        self.action = "Attaque"
                        self.reasoning = f"J'ai déjà défendu récemment. J'attaque la cible assignée."
                        self.last_action = "ATTACK"  # Track last action
                else:
                    action_id = 0  # HIT
                    self.action = "Attaque"
                    self.reasoning = f"Support. J'attaque la cible assignée."
                    self.last_action = "ATTACK"  # Track last action
            else:
                action_id = 0  # HIT
                self.action = "Attaque"
                self.reasoning = f"Par défaut. J'attaque la cible assignée."
                self.last_action = "ATTACK"  # Track last action

        target_id = self.get_target(targets=None, enemies=enemies)

        # Vérifier si la vie est basse pour changer d'arène
        if self.life < 5:
            # Changer d'arène en utilisant l'action 3
            new_arena_url, new_arena_id = self.find_new_arena()
            if new_arena_url and new_arena_id:
                action_id = 3  # ACTION ID pour changer d'arène
                self.action = "Changer d'Arène"
                self.reasoning = f"Vie faible ({self.life}). Je change d'arène vers {new_arena_id}."
                self.last_action = "SWITCH_ARENA"
                return action_id, new_arena_id
            else:
                self.reasoning += " Aucune arène disponible pour changer."

        return action_id, target_id

    def get_target(self, targets, enemies):
        if targets and self.cid in targets:
            target_id = targets[self.cid]
            # Vérifier si la cible est toujours vivante
            if any(char.get('cid') == target_id and not char.get('dead', False) for char in enemies):
                return target_id
        # Si aucune cible assignée ou la cible assignée est morte, choisir un ennemi au hasard
        if enemies:
            target_enemy = random.choice(enemies)
            return target_enemy.get('cid')
        return None

    def find_new_arena(self):
        # Chercher une nouvelle arène différente de l'actuelle
        available_arenas = [url for url in ARENA_MAPPING.keys() if url != self.arena_url]
        random.shuffle(available_arenas)
        for arena_url in available_arenas:
            arena_id = ARENA_MAPPING.get(arena_url)
            if arena_id:
                return arena_url, arena_id
        return None, None

    def perform_action(self, action_id, target_id):
        try:
            if action_id == 3:
                # Action spéciale pour changer d'arène
                print(f"[DEBUG] {self.bot_name} change d'arène vers ID {target_id}")
                response = requests.put(
                    f"{self.arena_url}/character/action/switcharena/{self.cid}/{action_id}/{target_id}"
                )
                response.raise_for_status()
                # Mise à jour de l'arène de l'agent
                new_arena_url = REVERSE_ARENA_MAPPING.get(target_id, self.arena_url)
                self.arena_url = new_arena_url
                self.arena_id = target_id
                self.action += f" (Action {action_id})"
                self.reasoning += f" Changement d'arène réussi."
                print(f"[INFO] {self.bot_name} a changé d'arène vers {self.arena_id}.")
            else:
                # Actions normales (HIT, BLOCK, DODGE)
                response = requests.post(
                    f"{self.arena_url}/character/action/{self.cid}/{action_id}/{target_id}"
                )
                response.raise_for_status()
                # Update last_action based on action_id
                if action_id in [1, 2]:
                    self.last_action = "DEFEND"
                else:
                    self.last_action = "ATTACK"
                self.action += f" (Action {action_id})"
                self.reasoning += f" Action réussie."
        except requests.exceptions.RequestException as e:
            self.action = "Action Échouée"
            self.reasoning = f"Échec de l'action: {e}"

    def get_enemy_actions(self, all_game_states, my_team):
        # Simuler la récupération des actions des ennemis
        enemy_actions = {}
        for arena_url, characters in all_game_states.items():
            for char in characters:
                if char.get('teamid') != my_team and not char.get('dead', False):
                    if char.get('life', 0) < 5:
                        enemy_actions[char.get('cid')] = 'Se Défend'
                    else:
                        enemy_actions[char.get('cid')] = 'HIT'
        return enemy_actions

if __name__ == "__main__":
    root = tk.Tk()
    app = AgentApp(root)
    root.mainloop()

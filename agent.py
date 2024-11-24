import requests
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
import random

# Configuration de l'API
API_URL = "http://127.0.0.1:5000"

class AgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent GUI")
        self.create_widgets()
        self.agents = []
        self.turn_logs = []
        self.turn_number = 0
        self.running = True

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
        columns = ("Bot Name", "Life", "Action", "Reasoning")
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

        # Créer les agents
        self.agents = self.create_agents(num_agents)

        # Lancer le thread de jeu
        threading.Thread(target=self.game_loop, daemon=True).start()

    def stop_agents(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def create_agents(self, num_agents):
        agents = []
        roles = ["Attacker", "Defender", "Support"]
        # Générer un team_id unique pour tous les agents
        team_id = self.get_unique_team_id()
        for i in range(num_agents):
            role = random.choice(roles)
            bot_name = f"{role}_{i+1}"
            agent = BotAgent(bot_name, team_id, num_agents, role)
            agents.append(agent)
        return agents

    def get_unique_team_id(self):
        try:
            response = requests.get(f"{API_URL}/characters/")
            response.raise_for_status()
            characters = response.json()['characters']
            existing_team_ids = set(char['teamid'] for char in characters)
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
                agent.reasoning
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

    def update_loop(self):
        while True:
            if self.agents:
                self.update_agents_table()
            time.sleep(1)

    def game_loop(self):
        self.running = True
        while self.running:
            self.turn_number += 1
            turn_log = {"turn": self.turn_number, "actions": []}
            print(f"\n=== TOUR {self.turn_number} ===")
            game_state = self.agents[0].get_game_state()
            # Mettre à jour la stratégie d'équipe
            targets = self.update_team_strategy(game_state)
            for agent in self.agents:
                if not self.running:
                    break
                agent.is_alive(game_state)
                if not agent.alive:
                    continue
                action_id, target_id = agent.decide_action(game_state, targets, self.agents, game_state, self.turn_number)
                if action_id is not None and target_id is not None:
                    agent.perform_action(action_id, target_id)
                turn_log["actions"].append({
                    "bot_name": agent.bot_name,
                    "life": agent.life,
                    "action": agent.action,
                    "reasoning": agent.reasoning
                })
            self.turn_logs.append(turn_log)
            self.update_logs()
            time.sleep(1)

    def update_team_strategy(self, game_state):
        # Cibler les ennemis en optimisant les dégâts
        agents_team_id = self.agents[0].team_id
        enemies = [char for char in game_state if char['teamid'] != agents_team_id and not char['dead']]
        if not enemies:
            return {}
        # Trier les ennemis par vie effective croissante
        enemies.sort(key=lambda x: x['life'] + x['armor'])
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
    BASE_URL = API_URL

    def __init__(self, bot_name, team_id, num_agents, role):
        self.bot_name = bot_name
        self.cid = None
        self.team_id = team_id
        self.num_agents = num_agents
        self.role = role
        self.life = 0
        self.action = "Attente"
        self.reasoning = ""
        self.alive = True
        self.strength = 0
        self.speed = 0
        self.create_agent()
        self.defense_counter = 0  # Compteur pour éviter les boucles de défense

    def create_agent(self):
        stats = self.allocate_stats()
        data = {
            "team_id": self.team_id,
            "arena_id": 1,
            "life": stats['life'],
            "strength": stats['strength'],
            "armor": stats['armor'],
            "speed": stats['speed']
        }
        try:
            response = requests.post(f"{self.BASE_URL}/character/join/", json=data)
            response.raise_for_status()
            self.cid = response.json()['cid']
            self.life = stats['life']
            self.strength = stats['strength']
            self.speed = stats['speed']
            print(f"[INFO] {self.bot_name} créé : ID = {self.cid}, Données = {data}")
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

        # Allouer les points restants en fonction des priorités
        while points_left > 0:
            for stat in priority:
                stats[stat] += 1
                points_left -= 1
                if points_left == 0:
                    break

        return stats

    def get_game_state(self):
        try:
            response = requests.get(f"{self.BASE_URL}/characters/")
            response.raise_for_status()
            return response.json()['characters']
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] {self.bot_name}: Impossible de récupérer l'état du jeu:\n{e}")
            return []

    def is_alive(self, game_state):
        my_character = next((char for char in game_state if char['cid'] == self.cid), None)
        if my_character and not my_character['dead']:
            self.alive = True
            self.life = my_character['life']
            return True
        else:
            self.alive = False
            self.action = "Mort"
            self.reasoning = "Je suis mort."
            return False

    def decide_action(self, game_state, targets, agents, full_game_state, turn_number):
        if not self.alive:
            return None, None
        my_character = next((char for char in game_state if char['cid'] == self.cid), None)
        if not my_character:
            self.alive = False
            self.action = "Mort"
            self.reasoning = "Personnage introuvable."
            return None, None
        self.life = my_character['life']
        my_life = self.life
        my_team = my_character['teamid']
        enemies = [char for char in game_state if char['teamid'] != my_team and not char['dead']]
        allies = [char for char in game_state if char['teamid'] == my_team and not char['dead']]
        if not enemies:
            self.action = "Attente"
            self.reasoning = "Aucun ennemi restant."
            return None, None

        # Vérifier si les ennemis attaquent
        enemy_actions = self.get_enemy_actions(full_game_state, my_team)
        under_attack = any(action in ['HIT', 'Action 0'] for action in enemy_actions.values())

        # Estimer si l'agent sera attaqué avant de pouvoir agir
        my_speed = my_character['speed']
        enemy_speeds = [enemy['speed'] for enemy in enemies]
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
            else:
                action_id = random.choice([1, 2])  # BLOCK ou DODGE
                self.action = "Se Défend"
                self.reasoning = f"Des ennemis plus rapides pourraient m'attaquer. Je me défends."
                self.defense_counter += 1
        else:
            self.defense_counter = 0
            if self.role == "Attacker":
                action_id = 0  # HIT
                self.action = "Attaque"
                self.reasoning = f"Attaquant. J'attaque la cible assignée."
            elif self.role == "Defender":
                if any(ally['life'] < 5 for ally in allies if ally['cid'] != self.cid):
                    ally_in_need = min([ally for ally in allies if ally['cid'] != self.cid], key=lambda x: x['life'])
                    action_id = random.choice([1, 2])  # BLOCK ou DODGE
                    target_id = ally_in_need['cid']
                    self.action = "Protège"
                    self.reasoning = f"Défenseur. Je protège l'allié {target_id[:4]}."
                    return action_id, target_id
                else:
                    action_id = 0  # HIT
                    self.action = "Attaque"
                    self.reasoning = f"Aucun allié en danger. J'attaque la cible assignée."
            elif self.role == "Support":
                # Le support peut soigner (s'il y a une action de soin) ou attaquer
                action_id = 0  # HIT
                self.action = "Attaque"
                self.reasoning = f"Support. J'attaque la cible assignée."
            else:
                action_id = 0  # HIT
                self.action = "Attaque"
                self.reasoning = f"Par défaut. J'attaque la cible assignée."

        target_id = targets.get(self.cid)
        if not target_id:
            # Si aucune cible assignée, choisir un ennemi au hasard
            target_enemy = random.choice(enemies)
            target_id = target_enemy['cid']

        return action_id, target_id

    def perform_action(self, action_id, target_id):
        try:
            response = requests.post(
                f"{self.BASE_URL}/character/action/{self.cid}/{action_id}/{target_id}"
            )
            response.raise_for_status()
            self.action += f" (Action {action_id})"
            self.reasoning += f" Action réussie."
        except requests.exceptions.RequestException as e:
            self.action = "Action Échouée"
            self.reasoning = f"Échec de l'action: {e}"

    def get_enemy_actions(self, full_game_state, my_team):
        # Simuler la récupération des actions des ennemis
        enemy_actions = {}
        for char in full_game_state:
            if char['teamid'] != my_team and not char['dead']:
                if char['life'] < 5:
                    enemy_actions[char['cid']] = 'Se Défend'
                else:
                    enemy_actions[char['cid']] = 'HIT'
        return enemy_actions

if __name__ == "__main__":
    root = tk.Tk()
    app = AgentApp(root)
    root.mainloop()

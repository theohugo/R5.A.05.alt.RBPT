# ApiArena - Projet Battle Royal

## Description

**ApiArena** est une API dédiée à la gestion d'un jeu de type Battle Royal. Elle permet de créer et gérer des personnages, d'organiser des combats, et d'optimiser les actions des agents. Ce projet inclut aussi un système de monitoring avec Kafka et Grafana pour une visualisation en temps réel des métriques.

## Fonctionnalités

- **API REST** :
  - Ajouter des personnages (POST)
  - Récupérer tous les personnages (GET)
  - Obtenir un personnage spécifique (GET)
  - Vérifier le statut du jeu (GET)
  - Supprimer tous les personnages (DELETE)
  - Ajouter une action et une cible (POST)
  
- **Engine** :
  - Refonte du système de priorisation des actions par vitesse.
  - Système de progression de dégâts par niveau.
  
- **Monitoring** :
  - Kafka pour la production et consommation de messages.
  - Grafana pour la visualisation des métriques (joueurs, actions, vie, etc.).


## Prérequis

- **Python 3.10+**
- **Flask**
- **Kafka**
- **Grafana**

## Installation

   ```bash
   git clone https://github.com/theohugo/R5.A.05.alt.RBPT.git
   ```
## Lancement de l'API

1. Installez les dépendances :

   ```bash
   cd R5.A.05.alt.RBPT/
   pip install -r requirements.txt
   ```
   
2. Lancez l'API avec Flask :

   ```bash
   flask run
   ```
   
## Lancer le visuel du serveur

1. Se placer dans le bon dossier
  ```bash
   cd R5.A.05.alt.RBPT/Project
   ```

2. Lancer le serveur
  ```bash
   python -m http.server 8000
   ```

   Pour acceder au visuel depuis le serveur 
   ```
   http://localhost:8000/Visual_RT/visual_server.html
   ```



## Configurez Kafka et Grafana selon la documentation.



3. Accédez à l'API sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

> ⚠️ **Note** : L'API tourne en mode développement. Utilisez un serveur WSGI comme Gunicorn pour une utilisation en production.

4. Lancer les tests unitaire de l'api :

   ```
   python -m unittest discover -s tests
   ```

## Contributeurs

- **RAGUIN Hugo**
- **BABEL Mickael**
- **TREHOU Nicolas**
- **PHAM HUYNH Tuong Vy**

## Ressources

- [Kafka Documentation](https://kafka.apache.org/)
- [Grafana Documentation](https://grafana.com/docs/)


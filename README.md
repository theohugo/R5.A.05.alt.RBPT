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

1. Clonez le projet :

   ```bash
   git clone https://github.com/theohugo/R5.A.05.alt.RBPT.git
   cd R5.A.05.alt.RBPT/Project
   ```

2. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

3. Configurez Kafka et Grafana selon la documentation.

## Lancement de l'API

1. Rendez-vous dans le répertoire `Engine` :

   ```bash
   cd ./Engine
   ```

2. Lancez l'API avec Flask :

   ```bash
   flask --app ApiArena run
   ```

3. Accédez à l'API sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

> ⚠️ **Note** : L'API tourne en mode développement. Utilisez un serveur WSGI comme Gunicorn pour une utilisation en production.

## Contributeurs

- **RAGUIN Hugo**
- **BABEL Mickael**

## Ressources

- [Kafka Documentation](https://kafka.apache.org/)
- [Grafana Documentation](https://grafana.com/docs/)


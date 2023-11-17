- le nom de la route
- la méthode (get, post, etc.)
- paramètres

ROUTES
------

- POST - ajouter un personnage à une arène - 
        /character/join/ - cid, teamid, life, strength, armor, speed

- POST - ajouter une action à un personnage
        /character/action/ - cid, action, target

- GET - récupérer un personnage - 
        /character/ - cid

- GET - récupérer les personnages d'une arène -
        /characters/

- GET - récupérer les résultats des matchs
        /status/ - numéro de tour


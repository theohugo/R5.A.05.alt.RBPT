import unittest
from app import app

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_say_hello(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello!', response.get_json().get('message'))

    def test_get_characters(self):
        response = self.app.get('/characters/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('characters', response.get_json())

    def test_create_character(self):
        character_data = {
            "team_id": 1,
            "arena_id": 2,
            "life": 5,
            "strength": 3,
            "armor": 3,
            "speed": 2
        }
        response = self.app.post('/character/join/', json=character_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('cid', response.get_json())

    def test_create_character_invalid(self):
        # Test avec des statistiques invalides
        invalid_data = {
            "team_id": 1,
            "arena_id": 2,
            "life": 10,
            "strength": 10,
            "armor": 10,
            "speed": 10  # Total > 20
        }
        response = self.app.post('/character/join/', json=invalid_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Total stats must not exceed 20', response.get_json().get('error'))

    def test_engine_status(self):
        response = self.app.get(f"/status/")
        self.assertEqual(response.status_code, 200)



    def test_update_character(self):
        # Ajouter des tests pour PUT (mettre à jour un personnage)
        pass

    def test_delete_character(self):
        # Ajouter des tests pour DELETE (supprimer un personnage)
        pass
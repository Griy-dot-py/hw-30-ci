import unittest
from fastapi.testclient import TestClient
from main import app


EXISTING_ID = 1
UNEXISTING_ID = 0

with TestClient(app) as client:
    
    class TestFastAPI(unittest.TestCase):
        @classmethod
        def setUpClass(cls) -> None:
            cls.client = client
        
        def setUp(self) -> None:
            response = self.client.get("/recipe/")
            json = json, *_ = response.json()
            self.views = json["views"]
        
        def test_get_all(self):
            response = self.client.get("/recipe/")
            self.assertEqual(response.status_code, 200)
        
        def test_views_increment(self):
            response = self.client.get("/recipe/")
            json = json, *_ = response.json()
            self.assertEqual(json["views"], self.views + 1)
        
        def test_get_one(self):
            response = self.client.get(f"/recipe/{EXISTING_ID}")
            self.assertEqual(response.status_code, 200)
        
        def test_not_get_unexisting(self):
            response = self.client.get(f"/recipes/{UNEXISTING_ID}")
            self.assertEqual(response.status_code, 404)
        
        def test_views_increment_after_single_call(self):
            self.client.get(f"/recipe/{EXISTING_ID}")
            response = self.client.get(f"/recipe/")
            json, *_ = response.json()
            self.assertEqual(json["views"], self.views + 2)

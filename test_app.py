"""
Unit tests for Rick and Morty Character API
"""

import unittest
from app import (
    app, RickAndMortyClient, filter_characters_by_origin, 
    sort_characters, paginate_characters, FILTERS
)
import json


class TestRickAndMortyAPI(unittest.TestCase):
    """Test cases for Rick and Morty API application"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("endpoints", data)
        self.assertIn("query_parameters", data)
        self.assertIn("filters", data)
        
    def test_characters_endpoint_default(self):
        """Test characters endpoint with default parameters"""
        response = self.client.get("/characters")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("data", data)
        self.assertIn("pagination", data)
        self.assertIn("filters", data)
        
    def test_characters_pagination(self):
        """Test pagination parameters"""
        response = self.client.get("/characters?page=1&limit=5")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertLessEqual(len(data["data"]), 5)
        self.assertEqual(data["pagination"]["limit"], 5)
        self.assertEqual(data["pagination"]["current_page"], 1)
        
    def test_characters_sorting_by_name(self):
        """Test sorting by name"""
        response = self.client.get("/characters?sort_by=name&sort_order=asc")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        characters = data["data"]
        if len(characters) > 1:
            names = [c["name"] for c in characters]
            self.assertEqual(names, sorted(names))
            
    def test_characters_sorting_by_id(self):
        """Test sorting by ID"""
        response = self.client.get("/characters?sort_by=id&sort_order=desc")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        characters = data["data"]
        if len(characters) > 1:
            ids = [c["id"] for c in characters]
            self.assertEqual(ids, sorted(ids, reverse=True))
            
    def test_invalid_page_parameter(self):
        """Test invalid page parameter"""
        response = self.client.get("/characters?page=-1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["pagination"]["current_page"], 1)
        
    def test_invalid_limit_parameter(self):
        """Test limit exceeds maximum"""
        response = self.client.get("/characters?limit=100")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertLessEqual(data["pagination"]["limit"], 50)
        
    def test_filter_characters_by_origin(self):
        """Test origin filtering logic"""
        test_characters = [
            {
                "name": "Rick",
                "species": "Human",
                "status": "Alive",
                "origin": {"name": "Earth (C-137)"}
            },
            {
                "name": "Jerry",
                "species": "Human",
                "status": "Alive",
                "origin": {"name": "Earth (Replacement Dimension)"}
            },
            {
                "name": "Unknown",
                "species": "Human",
                "status": "Alive",
                "origin": {"name": "Planet Blips and Chitz"}
            }
        ]
        
        filtered = filter_characters_by_origin(test_characters)
        self.assertEqual(len(filtered), 2)
        self.assertIn("Rick", [c["name"] for c in filtered])
        self.assertIn("Jerry", [c["name"] for c in filtered])
        self.assertNotIn("Unknown", [c["name"] for c in filtered])
        
    def test_sort_characters_by_name(self):
        """Test character sorting by name"""
        test_characters = [
            {"name": "Zoe", "id": 1},
            {"name": "Alice", "id": 2},
            {"name": "Bob", "id": 3}
        ]
        
        sorted_chars = sort_characters(test_characters, sort_by="name")
        names = [c["name"] for c in sorted_chars]
        self.assertEqual(names, ["Alice", "Bob", "Zoe"])
        
    def test_sort_characters_by_id_descending(self):
        """Test character sorting by ID descending"""
        test_characters = [
            {"name": "Zoe", "id": 1},
            {"name": "Alice", "id": 3},
            {"name": "Bob", "id": 2}
        ]
        
        sorted_chars = sort_characters(test_characters, sort_by="id", reverse=True)
        ids = [c["id"] for c in sorted_chars]
        self.assertEqual(ids, [3, 2, 1])
        
    def test_paginate_characters(self):
        """Test pagination logic"""
        test_characters = [{"id": i, "name": f"Char{i}"} for i in range(1, 26)]
        
        paginated, info = paginate_characters(test_characters, page=2, limit=10)
        self.assertEqual(len(paginated), 10)
        self.assertEqual(paginated[0]["id"], 11)
        self.assertEqual(info["current_page"], 2)
        self.assertEqual(info["total_items"], 25)
        self.assertEqual(info["total_pages"], 3)
        self.assertTrue(info["has_previous"])
        self.assertTrue(info["has_next"])
        
    def test_404_endpoint(self):
        """Test 404 error handling"""
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)
        
    def test_filters_applied(self):
        """Test that filters are applied correctly"""
        response = self.client.get("/characters?limit=1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        filters = data["filters"]
        self.assertEqual(filters["species"], "human")
        self.assertEqual(filters["status"], "alive")
        self.assertEqual(filters["origin"], "Earth (any variant)")


class TestRickAndMortyClient(unittest.TestCase):
    """Test cases for Rick and Morty API client"""
    
    def setUp(self):
        """Set up test client"""
        self.client = RickAndMortyClient()
        
    def test_client_initialization(self):
        """Test client initialization"""
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.base_url, "https://rickandmortyapi.com/api")
        
    def test_fetch_characters_real_api(self):
        """Test fetching characters from real API"""
        try:
            response = self.client.fetch_characters(status="alive", species="human")
            self.assertIn("results", response)
            self.assertIsInstance(response["results"], list)
        except Exception as e:
            self.skipTest(f"API not available: {str(e)}")


if __name__ == "__main__":
    unittest.main()

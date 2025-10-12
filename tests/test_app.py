import unittest
import json
import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_page(self):
        """Test that the home page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Code Assistant', response.data)
    
    def test_generate_missing_prompt(self):
        """Test that the API returns an error when no prompt is provided"""
        response = self.app.post('/generate', 
                                data=json.dumps({'model': 'openai'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_generate_invalid_model(self):
        """Test that the API returns an error when an invalid model is specified"""
        response = self.app.post('/generate', 
                                data=json.dumps({'prompt': 'Test prompt', 'model': 'invalid_model'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_local_model_placeholder(self):
        """Test that the local model placeholder returns some code"""
        response = self.app.post('/generate', 
                                data=json.dumps({'prompt': 'Test prompt', 'model': 'local'}),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('code', data)
        self.assertIn('placeholder', data['code'].lower())

if __name__ == '__main__':
    unittest.main()
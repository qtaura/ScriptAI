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

    def test_home_page(self):
        """Test that the home page loads correctly"""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI Code Assistant", response.data)

    def test_generate_missing_prompt(self):
        """Test that the API returns an error when no prompt is provided"""
        response = self.app.post(
            "/generate",
            data=json.dumps({"model": "openai"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_generate_invalid_model(self):
        """Test that the API returns an error when an invalid model is specified"""
        response = self.app.post(
            "/generate",
            data=json.dumps({"prompt": "Test prompt", "model": "invalid_model"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_local_model_placeholder(self):
        """Test that the local model returns a code stub"""
        response = self.app.post(
            "/generate",
            data=json.dumps({"prompt": "Test prompt", "model": "local"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("code", data)
        self.assertTrue(len(data["code"]) > 0)

    def test_invalid_json_payload(self):
        """Invalid JSON should return 400 with a clean error body."""
        response = self.app.post(
            "/generate",
            data="not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.data)
        self.assertIn("error", body)
        self.assertEqual(body["error"], "Invalid JSON payload")

    def test_unknown_model(self):
        """Unknown model should return 400 with clear message."""
        response = self.app.post(
            "/generate",
            data=json.dumps({"prompt": "x", "model": "nope"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.data)
        self.assertIn("error", body)
        self.assertTrue("Unknown model" in body["error"])

    def test_prometheus_metrics_endpoint(self):
        """Ensure /metrics exposes Prometheus text format when installed."""
        response = self.app.get("/metrics")
        # Accept either Prometheus content type or JSON error if client missing
        if response.status_code == 200:
            # Prometheus text should include HELP/TYPE or metric names
            body = response.data.decode("utf-8", errors="ignore")
            self.assertTrue("scriptai_requests_total" in body or "HELP" in body)
        else:
            data = json.loads(response.data)
            self.assertIn("error", data)

    def test_index_lists_local_model(self):
        """Index should list at least the local model option via adapters."""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.data.decode("utf-8", errors="ignore")
        self.assertIn('<option value="local">', body)


if __name__ == "__main__":
    unittest.main()

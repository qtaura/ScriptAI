import unittest
import json
import sys
import os
from unittest.mock import patch

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        # Ensure strict rate limit test mode is disabled by default
        app.config["RATELIMIT_STRICT_TEST"] = False

    def test_home_page(self):
        """Test that the home page loads correctly"""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        # SPA root should include the mount point
        self.assertIn(b'id="root"', response.data)

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

    def test_models_endpoint_lists_local_model(self):
        """Models API should include at least the local model option."""
        response = self.app.get("/models")
        self.assertEqual(response.status_code, 200)
        models = json.loads(response.data)
        self.assertTrue(any(m.get("id") == "local" for m in models))

    def test_generate_rate_limit_429(self):
        """/generate should return 429 after exceeding per-route limit."""
        # Enable strict test limits and use a unique client IP to avoid collisions
        app.config["RATELIMIT_STRICT_TEST"] = True
        headers = {"X-Forwarded-For": "203.0.113.55"}

        # First two requests should pass under "2 per minute"
        for i in range(2):
            r = self.app.post(
                "/generate",
                data=json.dumps({"prompt": "x", "model": "local"}),
                content_type="application/json",
                headers=headers,
            )
            self.assertNotEqual(r.status_code, 429)

        # Third request should hit the limit and return 429
        r = self.app.post(
            "/generate",
            data=json.dumps({"prompt": "x", "model": "local"}),
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(r.status_code, 429)
        body = json.loads(r.data)
        self.assertIn("error", body)

    def test_security_dangerous_prompt(self):
        """Dangerous content (script tags) should be rejected with 400."""
        response = self.app.post(
            "/generate",
            data=json.dumps(
                {"prompt": "<script>alert('x')</script>", "model": "local"}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.data)
        self.assertIn("error", body)
        self.assertTrue("dangerous" in body["error"].lower())

    def test_security_too_long_prompt(self):
        """Excessively long prompt should be rejected with 400."""
        long_prompt = "a" * 1200
        response = self.app.post(
            "/generate",
            data=json.dumps({"prompt": long_prompt, "model": "local"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.data)
        self.assertIn("error", body)
        self.assertTrue("too long" in body["error"].lower())

    def test_generate_prompt_non_string(self):
        """Non-string prompt should return 400."""
        response = self.app.post(
            "/generate",
            data=json.dumps({"prompt": 123, "model": "local"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.data)
        self.assertIn("error", body)
        self.assertIn("must be a string", body["error"])

    def test_adapter_error_openai_returns_502(self):
        """Upstream adapter error for OpenAI should return 502."""

        class FailingAdapter:
            def generate(self, prompt):
                return None, "Upstream error"

        with patch(
            "app.get_adapter",
            lambda model: FailingAdapter() if model == "openai" else None,
        ):
            # Ensure fallback is disabled for this test to assert original behavior
            app.config["ENABLE_FALLBACK"] = False
            response = self.app.post(
                "/generate",
                data=json.dumps({"prompt": "x", "model": "openai"}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 502)
        body = json.loads(response.data)
        self.assertIn("error", body)

    def test_fallback_to_local_on_openai_error(self):
        """When OpenAI fails and fallback is enabled, server should return code from local."""

        class FailingAdapter:
            def generate(self, prompt):
                return None, "Upstream error"

        class WorkingAdapter:
            def generate(self, prompt):
                return "// ok", None

        # Enable fallback and provide adapters for openai (fail) and local (success)
        app.config["ENABLE_FALLBACK"] = True

        with patch(
            "app.get_adapter",
            lambda model: FailingAdapter()
            if model == "openai"
            else (WorkingAdapter() if model == "local" else None),
        ):
            # Ensure available_models returns both openai and local
            with patch(
                "app.available_models",
                lambda: [
                    {"id": "openai", "name": "OpenAI"},
                    {"id": "local", "name": "Local Model"},
                ],
            ):
                response = self.app.post(
                    "/generate",
                    data=json.dumps({"prompt": "x", "model": "openai"}),
                    content_type="application/json",
                )
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.data)
        self.assertIn("code", body)
        self.assertEqual(body.get("model_used"), "local")
        self.assertEqual(body.get("fallback_from"), "openai")

    def test_adapter_exception_returns_500(self):
        """Unhandled adapter exception should be caught and return 500."""

        class ExplodingAdapter:
            def generate(self, prompt):
                raise RuntimeError("boom")

        with patch(
            "app.get_adapter",
            lambda model: ExplodingAdapter() if model == "local" else None,
        ):
            response = self.app.post(
                "/generate",
                data=json.dumps({"prompt": "x", "model": "local"}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 500)
        body = json.loads(response.data)
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()

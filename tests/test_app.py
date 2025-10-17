import unittest
import json
import sys
import os
from typing import Any, Dict
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

    def test_model_profiles_endpoint_structure(self):
        """Model profiles should include required fields and local provider."""
        response = self.app.get("/model-profiles")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertIn("models", data)
        models = data.get("models", [])
        self.assertTrue(
            any(isinstance(m, dict) and m.get("id") == "local" for m in models)
        )
        # Validate common fields on the local provider
        local: Dict[str, Any] = next((m for m in models if m.get("id") == "local"), {})
        for field in ["id", "name", "speed", "quality", "cost", "available"]:
            self.assertIn(field, local)

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

    def test_rate_limit_xff_multiple_ips_uses_first(self):
        """Limiter key should use first XFF entry; third request 429."""
        app.config["RATELIMIT_STRICT_TEST"] = True
        headers = {"X-Forwarded-For": "198.51.100.10, 198.51.100.2"}

        for _ in range(2):
            r = self.app.post(
                "/generate",
                data=json.dumps({"prompt": "x", "model": "local"}),
                content_type="application/json",
                headers=headers,
            )
            self.assertNotEqual(r.status_code, 429)

        r = self.app.post(
            "/generate",
            data=json.dumps({"prompt": "x", "model": "local"}),
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(r.status_code, 429)

    def test_rate_limit_xff_change_second_ip_does_not_bypass(self):
        """Changing second XFF IP should not evade limiter; expect 429 on third."""
        app.config["RATELIMIT_STRICT_TEST"] = True
        headers1 = {"X-Forwarded-For": "198.51.100.20, 198.51.100.2"}
        headers2 = {"X-Forwarded-For": "198.51.100.20, 203.0.113.9"}

        for _ in range(2):
            r = self.app.post(
                "/generate",
                data=json.dumps({"prompt": "x", "model": "local"}),
                content_type="application/json",
                headers=headers1,
            )
            self.assertNotEqual(r.status_code, 429)

        r = self.app.post(
            "/generate",
            data=json.dumps({"prompt": "x", "model": "local"}),
            content_type="application/json",
            headers=headers2,
        )
        self.assertEqual(r.status_code, 429)

    def test_rate_limit_xff_change_first_ip_resets_bucket(self):
        """Changing first XFF IP should hit a new bucket and pass."""
        app.config["RATELIMIT_STRICT_TEST"] = True
        h1 = {"X-Forwarded-For": "198.51.100.30, 198.51.100.2"}
        for _ in range(3):
            self.app.post(
                "/generate",
                data=json.dumps({"prompt": "x", "model": "local"}),
                content_type="application/json",
                headers=h1,
            )
        h2 = {"X-Forwarded-For": "198.51.100.99, 198.51.100.2"}
        r = self.app.post(
            "/generate",
            data=json.dumps({"prompt": "x", "model": "local"}),
            content_type="application/json",
            headers=h2,
        )
        self.assertNotEqual(r.status_code, 429)

    def test_sanitize_script_tag_removed(self):
        from scriptai.web.services.registry import security_manager

        s = "<script>alert('x')</script> Hello"
        sanitized = security_manager.sanitize_input(s)
        self.assertNotIn("<script", sanitized.lower())
        self.assertNotIn("</script>", sanitized.lower())

    def test_sanitize_javascript_url_removed(self):
        from scriptai.web.services.registry import security_manager

        s = "javascript:alert(1)"
        sanitized = security_manager.sanitize_input(s)
        self.assertNotIn("javascript:", sanitized.lower())

    def test_sanitize_html_escape_basic(self):
        from scriptai.web.services.registry import security_manager

        s = "<b>bold</b> & \"quoted\""
        sanitized = security_manager.sanitize_input(s)
        # Escaped brackets and ampersand should be present
        self.assertIn("&lt;b&gt;bold&lt;/b&gt;", sanitized)
        self.assertIn("&amp;", sanitized)
        self.assertIn("&quot;", sanitized)

    def test_validate_prompt_event_handler_blocked(self):
        from scriptai.web.services.registry import security_manager

        is_valid, err = security_manager.validate_prompt("onclick=alert(1)")
        self.assertFalse(is_valid)
        self.assertIsNotNone(err)

    def test_sanitize_handles_entity_obfuscation(self):
        from scriptai.web.services.registry import security_manager

        s = "java&#115;cript:alert(1)"
        sanitized = security_manager.sanitize_input(s)
        # Ensure entity remains escaped, preventing browser execution if rendered
        self.assertIn("java&amp;#115;cript:alert(1)", sanitized)

    # --- New tests for Smart Context Management ---
    def test_context_debug_inspect_present(self):
        headers = {"X-Conversation-Id": "conv-debug-1"}
        r = self.app.post(
            "/generate",
            data=json.dumps({"prompt": "First prompt", "model": "local", "debug": True}),
            content_type="application/json",
            headers=headers,
        )
        self.assertEqual(r.status_code, 200)
        body = json.loads(r.data)
        self.assertIn("context", body)
        ctx = body["context"]
        self.assertIn("messages_count", ctx)
        self.assertIn("summary_chars", ctx)
        self.assertIn("composed_chars", ctx)
        self.assertGreaterEqual(ctx.get("messages_count", 0), 1)

    def test_context_summarization_trims_messages(self):
        import app as app_module
        from scriptai.web.services.context import ContextManager

        # Replace the app's context manager with a test-friendly configuration
        app_module.context_manager = ContextManager(
            enabled=True, max_messages=3, summarize_after=4, max_summary_chars=500
        )

        headers = {"X-Conversation-Id": "conv-summarize-1"}
        for i in range(5):
            r = self.app.post(
                "/generate",
                data=json.dumps({
                    "prompt": f"Message {i} content for summarization purposes",
                    "model": "local",
                    "debug": True,
                }),
                content_type="application/json",
                headers=headers,
            )
            self.assertEqual(r.status_code, 200)
            last_body = json.loads(r.data)

        # After multiple messages, the manager should have summarized older ones
        self.assertIn("context", last_body)
        info = last_body["context"]
        self.assertLessEqual(info.get("messages_count", 0), 3)
        self.assertGreater(info.get("summary_chars", 0), 0)
        self.assertIsInstance(info.get("summary_preview", ""), str)


if __name__ == "__main__":
    unittest.main()

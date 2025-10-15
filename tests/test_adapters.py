import unittest
import sys
import os
import types
from typing import Any, cast
from unittest.mock import patch

# Add parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import model_adapters as m


class TestModelAdapters(unittest.TestCase):
    def test_openai_adapter_success_with_mock(self):
        """OpenAIAdapter.generate returns code when openai client is mocked."""

        class _FakeMessage:
            def __init__(self, content: str):
                self.content = content

        class _FakeChoice:
            def __init__(self, content: str):
                self.message = _FakeMessage(content)

        class _FakeResponse:
            def __init__(self, content: str):
                self.choices = [_FakeChoice(content)]

        class _FakeChatCompletion:
            @staticmethod
            def create(**kwargs):
                # Return deterministic code content without network calls
                return _FakeResponse("print('hello from openai mock')")

        # Create a fake openai module and mark it as Any for MyPy
        openai_fake = cast(Any, types.ModuleType("openai"))
        openai_fake.ChatCompletion = _FakeChatCompletion
        # Provide an empty error namespace to satisfy isinstance checks if reached
        openai_fake.error = types.SimpleNamespace()

        with patch.dict(sys.modules, {"openai": openai_fake}):
            with patch.object(m, "OPENAI_API_KEY", "test-key"):
                adapter = m.OpenAIAdapter()
                code, err = adapter.generate("Test prompt")
        self.assertIsNone(err)
        self.assertIsNotNone(code)
        code_str = cast(str, code)
        self.assertIn("hello from openai mock", code_str)

    def test_huggingface_adapter_success_with_mock(self):
        """HuggingFaceAdapter.generate returns code when requests is mocked."""

        class _FakeResponse:
            def __init__(self):
                self.status_code = 200

            def json(self):
                # Simulate HF response list with generated_text containing code block
                return [
                    {"generated_text": "```print('hello from hf mock')```"}
                ]

        def _fake_post(url, headers=None, json=None, timeout=None):
            return _FakeResponse()

        # Create a fake requests module and mark it as Any for MyPy
        requests_fake = cast(Any, types.ModuleType("requests"))
        requests_fake.post = _fake_post

        with patch.dict(sys.modules, {"requests": requests_fake}):
            with patch.object(m, "HUGGINGFACE_API_KEY", "test-key"):
                adapter = m.HuggingFaceAdapter()
                code, err = adapter.generate("Test prompt")
        self.assertIsNone(err)
        self.assertIsNotNone(code)
        code_str = cast(str, code)
        self.assertIn("hello from hf mock", code_str)

    def test_local_adapter_stub_generation(self):
        """LocalAdapter.generate returns a stub without network calls."""
        adapter = m.LocalAdapter()
        code, err = adapter.generate("Write a Python function to add two numbers")
        self.assertIsNone(err)
        self.assertIsNotNone(code)
        code_str = cast(str, code)
        self.assertTrue(len(code_str.strip()) > 0)


if __name__ == "__main__":
    unittest.main()
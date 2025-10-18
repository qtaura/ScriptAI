"""
Hello World Adapter Template for ScriptAI

Drop this file under `plugins/` (or set `SCRIPT_AI_PLUGINS_DIR`) to load it.
This demonstrates the minimal structure of a plugin with a custom adapter.
"""
from typing import Optional, Tuple

from model_adapters import ModelAdapter


class HelloWorldAdapter(ModelAdapter):
    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        code = (
            "# Hello from HelloWorldAdapter\n"
            f"# Prompt: {prompt}\n"
            "def hello_world():\n"
            "    print('hello from plugin')\n"
        )
        return code, None


def is_available() -> bool:
    """Signal adapter availability.
    For cloud providers, check environment (e.g., os.getenv('MY_API_KEY')).
    """
    return True


def register(register_adapter):
    """Register the adapter with ScriptAI.

    The loader calls this function and passes the `register_adapter` helper.
    """
    register_adapter(
        id="hello",
        name="Hello World Adapter",
        adapter_cls_or_factory=HelloWorldAdapter,
        is_available=is_available,
        description="Simple template adapter that returns a small Python stub.",
    )
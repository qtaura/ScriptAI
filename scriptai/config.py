"""
Environment and configuration helpers for ScriptAI.

Centralizes environment parsing to reduce duplication and implicit
side-effects across app and cli modules.
"""
from __future__ import annotations

import os
from typing import Optional, Callable

def load_env() -> None:
    """Load environment variables from a .env file if python-dotenv is installed."""
    loader: Optional[Callable[..., bool]] = None
    try:
        from dotenv import load_dotenv as _loader  # local import to avoid globals
        loader = _loader
    except Exception:  # pragma: no cover
        loader = None

    if loader is None:
        return
    try:
        loader()
    except Exception:
        # Never fail app startup due to env loading issues
        pass


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def enable_fallback_default() -> bool:
    """Default value for ENABLE_FALLBACK derived from environment."""
    return _env_bool("ENABLE_FALLBACK", True)


def get_api_keys() -> dict[str, Optional[str]]:
    """Fetch API keys from environment in a single place."""
    keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    }
    return keys


__all__ = [
    "load_env",
    "enable_fallback_default",
    "get_api_keys",
]
"""
ScriptAI core package.

This package provides shared helpers and integration points to decouple
the application from large root-level scripts. It enables a gradual
refactor toward a modular architecture without breaking existing imports.
"""

from typing import Any


def create_app(*args: Any, **kwargs: Any):
    """
    Lightweight factory shim returning the current Flask app instance.

    Kept minimal to preserve backwards compatibility while enabling a
    migration path to a full factory in future iterations.
    """
    # Lazy import to avoid circular imports during module initialization
    from app import app as _app

    return _app


__all__ = ["create_app"]
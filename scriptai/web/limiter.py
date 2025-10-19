"""
Flask-Limiter initialization helper with safe fallback.

This avoids hard dependencies and circular imports by constructing the
limiter instance from app.py.
"""
from __future__ import annotations

import os
from typing import Any

try:
    # Do not import Limiter globally to avoid optional dependency issues
    from flask_limiter import Limiter

    _HAS_LIMITER = True
except Exception:  # pragma: no cover
    _HAS_LIMITER = False


def init_limiter(app: Any) -> Any:
    """Initialize a Limiter instance or return a no-op substitute.

    The returned object exposes a `.limit` decorator used on routes.
    """
    if not _HAS_LIMITER:  # pragma: no cover
        return _NoopLimiter()

    # Import inside function to avoid import-time dependency for apps
    from flask import request

    def _rate_key_func() -> str:
        # Prefer X-Forwarded-For if present (behind proxies), else remote_addr
        xff = request.environ.get("HTTP_X_FORWARDED_FOR")
        if isinstance(xff, str) and xff:
            first = xff.split(",")[0].strip()
            if first:
                return first

        addr = request.remote_addr
        if isinstance(addr, str) and addr:
            return addr

        rem = request.environ.get("REMOTE_ADDR")
        if isinstance(rem, str) and rem:
            return rem

        return "127.0.0.1"

    try:
        storage_uri = os.getenv("RATELIMIT_STORAGE_URI")
    except Exception:
        storage_uri = None

    default_limit = os.getenv("RATELIMIT_DEFAULT", "100 per hour")
    if storage_uri:
        return Limiter(
            key_func=_rate_key_func,
            app=app,
            default_limits=[default_limit],
            storage_uri=storage_uri,
        )
    return Limiter(key_func=_rate_key_func, app=app, default_limits=[default_limit])


class _NoopLimiter:
    def limit(self, *args, **kwargs):  # pragma: no cover
        def _wrap(f):
            return f

        return _wrap


__all__ = ["init_limiter"]

"""
Catch-all Vercel Python function exposing the Flask WSGI app.

This ensures any request under `/api/*` is handled by the same Flask
application defined in `app.py`.

To avoid FUNCTION_INVOCATION_FAILED from import-time errors, we guard
the import and always return a valid WSGI response on failure.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, cast

# Simple WSGI type alias for mypy compatibility
WSGIApp = Callable[[dict[str, Any], Callable[..., Any]], Iterable[bytes]]

try:
    # Import the Flask WSGI application
    from app import app as _flask_app

    # Cast Flask instance to WSGI application for consistent typing
    handler_app: WSGIApp = cast(WSGIApp, _flask_app)
except Exception:
    # Fallback WSGI app that returns a 500 with the traceback
    import traceback

    _trace = traceback.format_exc()

    def _fallback_app(
        environ: dict[str, Any], start_response: Callable[..., Any]
    ) -> Iterable[bytes]:
        body = ("Import error while initializing Flask app:\n\n" + _trace).encode(
            "utf-8"
        )
        status = "500 Internal Server Error"
        headers = [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ]
        start_response(status, headers)
        return [body]

    handler_app = _fallback_app

# Expose as `app` for Vercel Python runtime with consistent type
app: WSGIApp = handler_app

# Explicit module export for clarity
__all__ = ["app"]
"""
Catch-all Vercel Python function exposing the Flask WSGI app.

This ensures any request under `/api/*` is handled by the same Flask
application defined in `app.py`.

To avoid FUNCTION_INVOCATION_FAILED from import-time errors, we guard
the import and always return a valid WSGI response on failure.
"""

try:
    # Import the Flask WSGI application
    from app import app as _flask_app

    # Expose as `app` for Vercel Python runtime
    app = _flask_app
except Exception:
    # Fallback WSGI app that returns a 500 with the traceback
    import traceback

    _trace = traceback.format_exc()

    def app(environ, start_response):
        body = ("Import error while initializing Flask app:\n\n" + _trace).encode("utf-8")
        status = "500 Internal Server Error"
        headers = [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ]
        start_response(status, headers)
        return [body]
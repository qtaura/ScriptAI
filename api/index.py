"""
Vercel Python entrypoint exposing the Flask WSGI app.

By defining an `app` variable that is a WSGI application, Vercel will route
requests under `/api/*` to this Flask app. The routes defined in `app.py`
like `/generate`, `/models`, etc., will be available as `/api/generate`,
`/api/models`, and so on.
"""

from app import app  # Flask WSGI application

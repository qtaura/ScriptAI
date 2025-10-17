from __future__ import annotations

import os
import hmac
from typing import Optional
from flask import request, jsonify, g


def init_auth(app) -> None:
    """
    Minimal auth scaffolding for multi-user deployments.

    - If `AUTH_TOKEN` env var is set, require either:
      - `Authorization: Bearer <token>` or
      - `X-API-Key: <token>`
    - GET requests remain open by default (docs, SPA, metrics).
      Adjust as needed for your deployment.
    - Sets `g.user_id` from `X-User-Id` header when provided.
    """

    def _auth_guard():
        token = os.getenv("AUTH_TOKEN")
        if not token:
            # Auth disabled by default; do nothing
            return None

        # Allow GET requests by default; tighten if desired
        if request.method == "GET":
            return None

        # Validate token via Authorization or X-API-Key
        auth = request.headers.get("Authorization", "")
        api_key = request.headers.get("X-API-Key")
        ok = False
        if auth.startswith("Bearer "):
            ok = hmac.compare_digest(auth[7:].strip(), token)
        elif isinstance(api_key, str) and api_key.strip():
            ok = hmac.compare_digest(api_key.strip(), token)

        if not ok:
            return jsonify({"error": "Unauthorized"}), 401

        # Bind user id if provided
        uid = request.headers.get("X-User-Id")
        if isinstance(uid, str) and uid.strip():
            g.user_id = uid.strip()
        else:
            g.user_id = "anonymous"

        return None

    # Register guard for all requests
    app.before_request(_auth_guard)


__all__ = ["init_auth"]

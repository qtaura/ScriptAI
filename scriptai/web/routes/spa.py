from __future__ import annotations

import os
from flask import Blueprint, jsonify, send_from_directory

bp = Blueprint("spa", __name__)


STATIC_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "static", "figmalol")
)


@bp.route("/")
def index():
    index_path = os.path.join(STATIC_ROOT, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(STATIC_ROOT, "index.html")
    return jsonify(
        {
            "message": "AI Code Assistant API",
            "endpoints": [
                "/models",
                "/model-profiles",
                "/generate",
                "/performance",
                "/metrics",
                "/metrics-json",
                "/security-stats",
                "/health",
                "/stats",
            ],
        }
    )


@bp.route("/ui/<path:filename>")
def serve_ui_asset(filename: str):
    if os.path.exists(os.path.join(STATIC_ROOT, filename)):
        return send_from_directory(STATIC_ROOT, filename)
    return jsonify({"error": "Not Found"}), 404


@bp.route("/assets/<path:filename>")
def serve_spa_assets(filename: str):
    assets_dir = os.path.join(STATIC_ROOT, "assets")
    if os.path.exists(os.path.join(assets_dir, filename)):
        return send_from_directory(assets_dir, filename)
    return jsonify({"error": "Not Found"}), 404


@bp.route("/vite.svg")
def serve_vite_svg():
    if os.path.exists(os.path.join(STATIC_ROOT, "vite.svg")):
        return send_from_directory(STATIC_ROOT, "vite.svg")
    return jsonify({"error": "Not Found"}), 404


@bp.route("/modelCards.json")
def serve_model_cards():
    if os.path.exists(os.path.join(STATIC_ROOT, "modelCards.json")):
        return send_from_directory(STATIC_ROOT, "modelCards.json")
    return jsonify({"error": "Not Found"}), 404
from __future__ import annotations

from flask import Blueprint, jsonify

from scriptai.web.services.registry import analytics_service

bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


@bp.get("/")
def get_analytics_summary():
    summary = analytics_service.get_summary()
    return jsonify(summary)


@bp.get("/session/<context_key>")
def get_session_analytics(context_key: str):
    data = analytics_service.get_session_analytics(context_key)

    total_requests = data.get("total_requests", 0)
    total_sessions = data.get("total_sessions", 0)
    total_errors = data.get("total_errors", 0)

    models_used = data.get("models_used", [])
    primary_model = data.get("primary_model")

    consistent = data.get("consistent", False)

    return jsonify(
        {
            "total_requests": total_requests,
            "total_sessions": total_sessions,
            "total_errors": total_errors,
            "models_used": models_used,
            "primary_model": primary_model,
            "consistent": bool(consistent),
            "context_key": context_key,
        }
    )
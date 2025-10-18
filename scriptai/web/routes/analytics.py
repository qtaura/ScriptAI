from __future__ import annotations

from typing import Any, Dict
from flask import Blueprint, jsonify, request, g

from scriptai.web.services.registry import context_manager, monitoring_manager

# Serve at root to match SPA fetch("/session-analytics")
bp = Blueprint("analytics", __name__)


@bp.route("/session-analytics", methods=["GET"])  # frontend expects this path
def get_session_analytics():
    client_ip = request.environ.get("REMOTE_ADDR") or request.remote_addr or "127.0.0.1"
    conv_id = request.headers.get("X-Conversation-Id")
    user_id = getattr(g, "user_id", None)
    context_key = (conv_id or user_id or client_ip) or "unknown"

    stats = context_manager.get_stats(context_key)
    messages_count = int(stats.get("messages_count", 0))
    content_chars = int(stats.get("content_chars", 0))
    summary_chars = int(stats.get("summary_chars", 0))

    # Simple token estimate (~4 chars per token)
    tokens_estimated = int(round((content_chars + summary_chars) / 4))

    # Aggregate model usage from recent performance metrics
    hist = list(getattr(monitoring_manager, "performance_metrics", []))
    models_used: Dict[str, int] = {}
    for m in hist:
        model_name = m.get("model") if isinstance(m, dict) else None
        if isinstance(model_name, str) and model_name:
            models_used[model_name] = models_used.get(model_name, 0) + 1

    primary_model = (
        max(models_used.items(), key=lambda kv: kv[1])[0] if models_used else None
    )

    consistent = bool(primary_model is not None and len(models_used) == 1)

    return jsonify(
        {
            "messages_count": messages_count,
            "tokens_estimated": tokens_estimated,
            "models_used": models_used,
            "primary_model": primary_model,
            "consistent": consistent,
            "context_key": context_key,
        }
    )

from __future__ import annotations

from flask import Blueprint, jsonify, request, g

from scriptai.web.services.registry import (
    context_manager,
    monitoring_manager,
)

bp = Blueprint("analytics", __name__)


@bp.route("/session-analytics", methods=["GET"])  # simple GET endpoint for UI
def session_analytics():
    # Determine client IP (consistent with /generate route)
    xff = request.environ.get("HTTP_X_FORWARDED_FOR")
    if isinstance(xff, str) and xff.strip():
        client_ip: str = xff.split(",")[0].strip()
    else:
        addr = request.remote_addr
        if isinstance(addr, str) and addr:
            client_ip = addr
        else:
            rem = request.environ.get("REMOTE_ADDR")
            client_ip = rem if isinstance(rem, str) and rem else "127.0.0.1"

    # Context key derivation: conversation -> user -> IP
    conv_id = request.headers.get("X-Conversation-Id") or request.args.get(
        "conversation_id"
    )
    user_id = getattr(g, "user_id", None)
    context_key = (conv_id or user_id or client_ip) or "unknown"

    # Gather context stats (message count, content char length)
    try:
        stats = context_manager.get_stats(context_key)
    except Exception:
        stats = {"messages_count": 0, "content_chars": 0}

    # Approximate tokens from character count (~4 chars per token)
    content_chars = int(stats.get("content_chars", 0) or 0)
    tokens_estimated = (content_chars + 3) // 4

    # Aggregate model usage for this client IP from performance metrics
    models_used: dict[str, int] = {}
    try:
        for m in list(monitoring_manager.performance_metrics):
            if m.get("client_ip") == client_ip and m.get("success"):
                model = m.get("model") or "unknown"
                models_used[model] = models_used.get(model, 0) + 1
    except Exception:
        # Best-effort only; never crash analytics
        pass

    total_model_events = sum(models_used.values())
    primary_model = None
    if models_used:
        primary_model = max(models_used.items(), key=lambda kv: kv[1])[0]
    consistent = len(models_used.keys()) <= 1 and total_model_events > 0

    return jsonify(
        {
            "messages_count": int(stats.get("messages_count", 0) or 0),
            "tokens_estimated": int(tokens_estimated),
            "models_used": models_used,
            "primary_model": primary_model,
            "consistent": bool(consistent),
            "context_key": context_key,
        }
    )
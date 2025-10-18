from __future__ import annotations

import os
from typing import Any

from flask import Flask, g, request

from scriptai.config import (
    get_cors_config,
    get_rate_limit_config,
    load_env,
    enable_fallback_default,
)
from scriptai.web.routes.metrics import bp as metrics_bp
from scriptai.web.routes.models import bp as models_bp
from scriptai.web.routes.spa import bp as spa_bp
from scriptai.web.routes.analytics import bp as analytics_bp
from scriptai.web.services.registry import monitoring_manager, security_manager
from scriptai.web.auth import init_auth


def _apply_security_headers(response):
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "connect-src 'self' http://localhost:5000 https://*; "
        "frame-ancestors 'none';"
    )
    response.headers["Content-Security-Policy"] = csp_policy
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


def _validate_environment_on_startup(app: Flask) -> None:
    logger = monitoring_manager.logger
    logger.info("Validating environment configuration...")
    required = [
        # Not all keys are strictly required at the same time; this is advisory.
        # Each adapter will validate its own key usage, but we log presence here.
        "OPENAI_API_KEY",
        "HUGGINGFACE_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
    ]
    for key in required:
        if os.getenv(key):
            logger.info(f"Env {key} detected")
        else:
            logger.info(f"Env {key} not set")


def create_app() -> Flask:
    load_env()

    app = Flask(__name__)

    # Initialize optional auth guard (enabled when AUTH_TOKEN is set)
    init_auth(app)

    # Basic config
    app.config.setdefault("JSON_SORT_KEYS", False)
    app.config.setdefault("ENABLE_FALLBACK", enable_fallback_default())
    # Read strict rate limit test flag from environment (default False)
    try:
        strict_val = os.getenv("RATELIMIT_STRICT_TEST")
        if strict_val is not None:
            app.config["RATELIMIT_STRICT_TEST"] = strict_val.strip().lower() in (
                "1",
                "true",
                "yes",
                "on",
            )
        else:
            app.config.setdefault("RATELIMIT_STRICT_TEST", False)
    except Exception:
        app.config.setdefault("RATELIMIT_STRICT_TEST", False)

    # CORS (if using flask-cors elsewhere, omitted here to avoid new deps)
    cors_cfg = get_cors_config()
    app.config["CORS_ORIGINS"] = cors_cfg.get("origins", ["*"])

    # Security hooks and request metadata
    @app.before_request
    def _start_timer():
        g.start_time = monitoring_manager.now()

    @app.before_request
    def _assign_request_id():
        g.request_id = monitoring_manager.new_request_id()

    @app.after_request
    def _after(resp):
        duration = monitoring_manager.since(g.get("start_time"))
        monitoring_manager.observe_request(
            method=request.method,
            path=request.path,
            status=resp.status_code,
            duration=duration,
        )
        return _apply_security_headers(resp)

    # Blueprints
    app.register_blueprint(spa_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(analytics_bp)

    _validate_environment_on_startup(app)

    return app
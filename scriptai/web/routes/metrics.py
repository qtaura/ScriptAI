from __future__ import annotations

from flask import Blueprint, jsonify, Response

from scriptai.monitoring.prometheus import generate_latest, CONTENT_TYPE_LATEST
from scriptai.web.services.registry import (
    monitoring_manager,
    security_manager,
)

bp = Blueprint("metrics", __name__)


@bp.route("/performance")
def get_performance():
    metrics = monitoring_manager.get_performance_metrics()
    return jsonify(metrics)


@bp.route("/metrics")
def prometheus_metrics():
    if generate_latest is None:
        return jsonify({"error": "Prometheus client not installed"}), 500
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@bp.route("/metrics-json")
def get_metrics_json():
    return jsonify(
        {
            "usage": monitoring_manager.get_usage_stats(hours=24),
            "performance": monitoring_manager.get_performance_metrics(),
            "health": monitoring_manager.check_health(),
        }
    )


@bp.route("/security-stats")
def get_security_stats():
    stats = security_manager.get_security_stats()
    return jsonify(stats)
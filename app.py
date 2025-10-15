from flask import Flask, render_template, request, jsonify, Response, g, send_from_directory
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # for type hints only; avoids runtime import issues
    from flask_limiter import Limiter as LimiterType
import os
import requests
import time
from dotenv import load_dotenv
from typing import Optional, Callable
from model_adapters import get_adapter, available_models
from security import SecurityManager
from monitoring import MonitoringManager

# Prometheus client (optional)
generate_latest: Optional[Callable[[], bytes]]
CONTENT_TYPE_LATEST: str
try:
    from prometheus_client import (
        generate_latest as _generate_latest,
        CONTENT_TYPE_LATEST as _CONTENT_TYPE_LATEST,
    )

    generate_latest = _generate_latest
    CONTENT_TYPE_LATEST = _CONTENT_TYPE_LATEST
except ImportError:  # pragma: no cover
    generate_latest = None
    CONTENT_TYPE_LATEST = "text/plain; charset=utf-8"

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Performance-related config
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = False
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 300
app.config.setdefault("RATELIMIT_STRICT_TEST", False)

# Initialize security and monitoring
security_manager = SecurityManager()
monitoring_manager = MonitoringManager()

# Configure rate limiting (Flask-Limiter) with sane defaults
limiter: Any
try:
    from flask_limiter import Limiter

    _has_limiter = True
except Exception:  # pragma: no cover
    _has_limiter = False

if _has_limiter:

    def _rate_key_func():
        # Prefer X-Forwarded-For if present (behind proxies), else remote_addr
        return request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)

    limiter = Limiter(key_func=_rate_key_func, app=app, default_limits=["100 per hour"])
else:

    class _NoopLimiter:
        def limit(self, *args, **kwargs):
            def _wrap(f):
                return f

            return _wrap

    limiter = _NoopLimiter()


@app.before_request
def _start_timer():
    g._start_time = time.time()


@app.after_request
def set_security_headers(response):
    """Apply security headers to all responses"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    # Allow CDN for Prism assets
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://cdnjs.cloudflare.com; "
        "style-src 'self' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com"
    )
    # Record request metrics
    try:
        start_time = getattr(g, "_start_time", None)
        if start_time is not None:
            duration = time.time() - start_time
            endpoint = request.path
            method = request.method
            status = response.status_code
            # Use MonitoringManager's Prometheus metrics if available
            rc = getattr(monitoring_manager, "request_counter", None)
            rl = getattr(monitoring_manager, "request_latency", None)
            if rc is not None and rl is not None:
                rc.labels(endpoint=endpoint, method=method, status=str(status)).inc()
                rl.labels(endpoint=endpoint, method=method, status=str(status)).observe(
                    duration
                )
    except Exception:
        pass

    return response


@app.route("/")
def index():
    # Serve the new React-built SPA as the main UI
    return send_from_directory("static/figmalol", "index.html")


# Serve the React-built UI (SPA) from static/figmalol
@app.route("/ui/new")
def ui_new_index():
    return send_from_directory("static/figmalol", "index.html")


@app.route("/ui/<path:filename>")
def ui_new_assets(filename: str):
    # Serve assets referenced relatively by the SPA, e.g., /ui/assets/*
    return send_from_directory("static/figmalol", filename)


# Root-level assets used by the SPA when served from '/'
@app.route("/assets/<path:filename>")
def spa_assets(filename: str):
    return send_from_directory("static/figmalol/assets", filename)


@app.route("/vite.svg")
def spa_vite_svg():
    return send_from_directory("static/figmalol", "vite.svg")


@app.route("/models")
def get_models():
    """Expose available models for the React UI."""
    return jsonify(available_models())


def generate_with_openai(prompt):
    """Deprecated: use adapters. Kept for backward compatibility."""
    adapter = get_adapter("openai")
    return adapter.generate(prompt) if adapter else (None, "Unknown model: openai")


def generate_with_huggingface(prompt):
    """Deprecated: use adapters. Kept for backward compatibility."""
    adapter = get_adapter("huggingface")
    return adapter.generate(prompt) if adapter else (None, "Unknown model: huggingface")


def _detect_language(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in ["python", "pandas", "fastapi", "def "]):
        return "python"
    if any(k in p for k in ["react", "javascript", "node", "function "]):
        return "javascript"
    if any(k in p for k in ["sql", "select", "from", "where"]):
        return "sql"
    if any(k in p for k in ["html", "css", "<!doctype", "<html"]):
        return "html"
    return "python"


def _generate_stub(lang: str, prompt: str) -> str:
    if lang == "python":
        return (
            "def generated_function(*args, **kwargs):\n"
            "    \"\"\"\n"
            f"    Generated locally based on prompt: {prompt}\n"
            "    Replace this stub with your implementation.\n"
            "    \"\"\"\n"
            "    # TODO: implement logic based on requirements above\n"
            "    return None\n"
        )
    if lang == "javascript":
        return (
            "// Generated locally based on prompt\n"
            f"// {prompt}\n"
            "export function generatedFunction(...args) {\n"
            "  // TODO: implement logic based on requirements above\n"
            "  return null;\n"
            "}\n"
        )
    if lang == "sql":
        return (
            "-- Generated locally based on prompt\n"
            f"-- {prompt}\n"
            "SELECT 1 AS placeholder;\n"
        )
    if lang == "html":
        return (
            "<!-- Generated locally based on prompt -->\n"
            f"<!-- {prompt} -->\n"
            "<!DOCTYPE html><html><head>"
            "<meta charset=\"utf-8\">"
            "<title>Generated</title>"
            "</head>\n"
            "<body>"
            "<div id=\"app\">Replace this stub with your implementation</div>"
            "</body></html>\n"
        )
    return _generate_stub("python", prompt)


def generate_with_local_model(prompt):
    """Deprecated: use adapters. Kept for backward compatibility."""
    adapter = get_adapter("local")
    return adapter.generate(prompt) if adapter else (None, "Unknown model: local")


def _json_error(message: str, status: int):
    """Return a minimal JSON error response with given HTTP status."""
    return jsonify({"error": message}), status


# JSON handler for 429 Too Many Requests
@app.errorhandler(429)
def _handle_rate_limit(e):  # pragma: no cover (exercised via tests)
    try:
        monitoring_manager.log_error(
            "rate_limit_exceeded", str(e), {"client_ip": request.remote_addr}
        )
    except Exception:
        pass
    return _json_error("Rate limit exceeded. Try again later.", 429)


def _generate_limit():
    # Stricter limit during tests to verify 429 behavior without impacting production
    return "2 per minute" if app.config.get("RATELIMIT_STRICT_TEST") else "100 per hour"


@app.route("/generate", methods=["POST"])
@limiter.limit(_generate_limit)
def generate_code():
    start_time = time.time()
    client_ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)

    try:
        # Get the prompt and model from the request
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return _json_error("Invalid JSON payload", 400)

        prompt = data.get("prompt")
        model = data.get("model", "openai")

        if not isinstance(prompt, str):
            return _json_error("'prompt' must be a string", 400)

        # Security validation
        is_valid, error_msg = security_manager.validate_prompt(prompt)
        if not is_valid:
            security_manager.log_security_event(
                "invalid_prompt", error_msg or "Unknown error", client_ip
            )
            return _json_error(error_msg or "Invalid prompt", 400)

        # Rate limiting
        within_limit, rate_error = security_manager.check_rate_limit(
            client_ip or "unknown"
        )
        if not within_limit:
            security_manager.log_security_event(
                "rate_limit_exceeded", rate_error or "Rate limit exceeded", client_ip
            )
            return _json_error(rate_error or "Rate limit exceeded", 429)

        if not prompt.strip():
            return _json_error("No prompt provided", 400)

        # Generate code based on selected model using adapters
        adapter = get_adapter(model)
        if adapter is None:
            return _json_error(f"Unknown model: {model}", 400)
        code, error = adapter.generate(prompt)

        response_time = time.time() - start_time

        # Log the request
        monitoring_manager.log_request(
            model=model,
            prompt_length=len(prompt),
            response_time=response_time,
            success=error is None,
            client_ip=client_ip,
            error=error,
        )

        if error:
            # Upstream provider errors: return as clean JSON, 502
            status_code = 502 if model in {"openai", "huggingface"} else 500
            return _json_error(error, status_code)

        return jsonify({"code": code})

    except Exception as e:
        response_time = time.time() - start_time
        monitoring_manager.log_error(
            "unexpected_error", str(e), {"client_ip": client_ip}
        )
        monitoring_manager.log_request(
            model="unknown",
            prompt_length=0,
            response_time=response_time,
            success=False,
            client_ip=client_ip,
            error=str(e),
        )
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/health")
def health_check():
    """Health check endpoint"""
    health_status = monitoring_manager.check_health()
    return jsonify(health_status)


@app.route("/stats")
def get_stats():
    """Get usage statistics"""
    stats = monitoring_manager.get_usage_stats(hours=24)
    return jsonify(stats)


@app.route("/performance")
def get_performance():
    """Get performance metrics"""
    metrics = monitoring_manager.get_performance_metrics()
    return jsonify(metrics)


@app.route("/metrics")
def prometheus_metrics():
    """Expose Prometheus metrics in the standard text format."""
    if generate_latest is None:
        return jsonify({"error": "Prometheus client not installed"}), 500
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/metrics-json")
def get_metrics_json():
    """Get combined metrics for dashboard as JSON."""
    return jsonify(
        {
            "usage": monitoring_manager.get_usage_stats(hours=24),
            "performance": monitoring_manager.get_performance_metrics(),
            "health": monitoring_manager.check_health(),
        }
    )


@app.route("/security-stats")
def get_security_stats():
    """Get security statistics"""
    stats = security_manager.get_security_stats()
    return jsonify(stats)


def main():
    """GUI script entry point for running the Flask app."""
    app.run(debug=True)


if __name__ == "__main__":
    main()

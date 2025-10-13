from flask import Flask, render_template, request, jsonify, Response, g
import os
import requests
import time
from dotenv import load_dotenv
from typing import Optional, Callable
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

# Initialize security and monitoring
security_manager = SecurityManager()
monitoring_manager = MonitoringManager()


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
        "style-src 'self' https://cdnjs.cloudflare.com"
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
    # Pass available models to the template
    models = []
    if OPENAI_API_KEY:
        models.append({"id": "openai", "name": "OpenAI GPT-3.5"})
    if HUGGINGFACE_API_KEY:
        models.append({"id": "huggingface", "name": "HuggingFace StarCoder"})
    models.append({"id": "local", "name": "Local Model (Placeholder)"})

    return render_template("index.html", models=models)


def generate_with_openai(prompt):
    """Generate code using OpenAI API"""
    import openai

    if not OPENAI_API_KEY:
        return (
            None,
            (
                "OpenAI API key not found. "
                "Please set the OPENAI_API_KEY environment variable."
            ),
        )

    openai.api_key = OPENAI_API_KEY

    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that generates code based on "
                    "user requirements. Provide only the code with minimal "
                    "explanation."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1500,
            temperature=0.7,
        )

        return response.choices[0].message.content, None
    except Exception as e:
        return None, f"Error with OpenAI API: {str(e)}"


def generate_with_huggingface(prompt):
    """Generate code using HuggingFace Inference API (free alternative)"""
    if not HUGGINGFACE_API_KEY:
        return (
            None,
            (
                "HuggingFace API key not found. "
                "Please set the HUGGINGFACE_API_KEY environment variable."
            ),
        )

    API_URL = "https://api-inference.huggingface.co/models/bigcode/starcoder"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

    # Prepare the prompt for code generation
    full_prompt = f"Generate code for the following request: {prompt}\n\n```"

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={
                "inputs": full_prompt,
                "parameters": {"max_new_tokens": 500, "return_full_text": False},
            },
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            # Extract the generated code
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                # Clean up the response to extract just the code
                if "```" in generated_text:
                    # Extract code between backticks if present
                    code_parts = generated_text.split("```")
                    if len(code_parts) >= 2:
                        return code_parts[1].strip(), None
                return generated_text.strip(), None
            return "No code generated", None
        else:
            return None, f"Error: API returned status code {response.status_code}"
    except Exception as e:
        return None, f"Error with HuggingFace API: {str(e)}"


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
    """Generate code using a local model (basic stub implementation)"""
    lang = _detect_language(prompt)
    return _generate_stub(lang, prompt), None


def _json_error(message: str, status: int):
    """Return a minimal JSON error response with given HTTP status."""
    return jsonify({"error": message}), status


@app.route("/generate", methods=["POST"])
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

        # Generate code based on selected model
        if model == "openai":
            code, error = generate_with_openai(prompt)
        elif model == "huggingface":
            code, error = generate_with_huggingface(prompt)
        elif model == "local":
            code, error = generate_with_local_model(prompt)
        else:
            return _json_error(f"Unknown model: {model}", 400)

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

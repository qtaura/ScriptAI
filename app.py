from __future__ import annotations

from flask import (
    request,
    jsonify,
    Response,
    g,
    stream_with_context,
)
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # for type hints only; avoids runtime import issues
    from flask_limiter import Limiter as LimiterType
import time
from typing import Optional, Callable
from model_adapters import get_adapter, available_models
from scriptai.web.services.registry import (
    security_manager,
    monitoring_manager,
    context_manager,
)
from scriptai.web.app import create_app
import os

# Initialize Flask app via factory
app = create_app()


## Environment validation is handled in the app factory

# Configure rate limiting (Flask-Limiter) with sane defaults
from scriptai.web.limiter import init_limiter

limiter: Any = init_limiter(app)


## SPA and models endpoints are now served via blueprints in scriptai.web.routes


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


def _available_model_ids() -> list:
    """Return list of available model IDs using adapters helper.

    Falls back to ["local"] on any error to ensure at least one candidate exists.
    """
    try:
        models = available_models()
        if isinstance(models, list):
            return [m.get("id") for m in models if isinstance(m, dict) and m.get("id")]
    except Exception:
        pass
    return ["local"]


def _is_truthy(val: object) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        return val.strip().lower() in {"1", "true", "yes", "on"}
    return False


def _smart_route_model(prompt: str, available: list[str]) -> tuple[str, str, list[str]]:
    """Choose a model based on prompt characteristics and availability.

    Returns (chosen_model, reason, ranked_candidates).
    """
    p = prompt.lower()
    length = len(p)

    # Language/topic hints
    is_python = any(k in p for k in ["python", "pandas", "fastapi", "def "])
    is_js = any(k in p for k in ["react", "javascript", "node", "function "])
    is_sql = any(k in p for k in ["sql", "select ", " from ", " where "])

    # Simple priority lists by scenario
    long_prompt = length > 500
    if long_prompt:
        # Prefer models known for larger context windows first
        preference = ["anthropic", "gemini", "openai", "huggingface", "local"]
        reason = "long prompt; prioritize larger-context providers"
    elif is_js:
        preference = ["openai", "gemini", "anthropic", "huggingface", "local"]
        reason = "javascript/react hints; prioritize OpenAI/Gemini"
    elif is_python or is_sql:
        preference = ["openai", "anthropic", "huggingface", "gemini", "local"]
        reason = "python/sql hints; prioritize OpenAI/Anthropic"
    else:
        preference = ["openai", "anthropic", "gemini", "huggingface", "local"]
        reason = "general prompt; default provider order"

    candidates = [m for m in preference if m in set(available)]
    chosen = candidates[0] if candidates else "local"
    return chosen, reason, candidates


# JSON handler for 429 Too Many Requests
@app.errorhandler(429)
def _handle_rate_limit(e):  # pragma: no cover (exercised via tests)
    try:
        monitoring_manager.log_error(
            "rate_limit_exceeded",
            str(e),
            {"client_ip": request.remote_addr},
            request_id=getattr(g, "request_id", None),
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
    # Harden client IP extraction: honor first XFF entry only
    xff = request.environ.get("HTTP_X_FORWARDED_FOR")
    if isinstance(xff, str) and xff.strip():
        client_ip: str = xff.split(",")[0].strip()
    else:
        # Ensure a strict string type for mypy: fall back to REMOTE_ADDR or localhost
        addr = request.remote_addr
        if isinstance(addr, str) and addr:
            client_ip = addr
        else:
            rem = request.environ.get("REMOTE_ADDR")
            client_ip = rem if isinstance(rem, str) and rem else "127.0.0.1"

    try:
        # Get the prompt and model from the request
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return _json_error("Invalid JSON payload", 400)

        prompt = data.get("prompt")
        model = data.get("model", "openai")
        debug = (
            _is_truthy(data.get("debug"))
            or _is_truthy(request.args.get("debug"))
            or _is_truthy(request.headers.get("X-Debug-Decision"))
        )

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

        # Sanitize input before passing to model adapters
        sanitized_prompt = security_manager.sanitize_input(prompt)

        # Determine context key (conversation -> user -> IP) and record user message
        conv_id = (
            data.get("conversation_id")
            or data.get("conversationId")
            or request.headers.get("X-Conversation-Id")
        )
        user_id = getattr(g, "user_id", None)
        context_key = (conv_id or user_id or client_ip) or "unknown"
        context_manager.add_message(context_key, "user", sanitized_prompt)
        composed_prompt = context_manager.compose_prompt(context_key, sanitized_prompt)

        # Determine model: support explainable smart routing when model == "auto"
        router_info = None
        selected_model = model
        if model == "auto":
            available_ids = _available_model_ids()
            chosen, reason, ranked = _smart_route_model(sanitized_prompt, available_ids)
            selected_model = chosen
            if debug:
                router_info = {
                    "mode": "auto",
                    "chosen": chosen,
                    "reason": reason,
                    "candidates": ranked,
                    "available": available_ids,
                }

        # Generate code based on selected/explicit model using adapters
        adapter = get_adapter(selected_model)
        if adapter is None:
            return _json_error(f"Unknown model: {selected_model}", 400)
        code, error = adapter.generate(composed_prompt)

        response_time = time.time() - start_time

        # Log the request
        monitoring_manager.log_request(
            model=selected_model,
            prompt_length=len(prompt),
            response_time=response_time,
            success=error is None,
            client_ip=client_ip,
            error=error,
            request_id=getattr(g, "request_id", None),
        )

        if error:
            # Attempt fallback to a backup model when enabled
            try:
                if bool(app.config.get("ENABLE_FALLBACK", True)):
                    # Preferred order: keep primary first to preserve selection, then try others
                    preferred_order = [
                        "openai",
                        "anthropic",
                        "gemini",
                        "huggingface",
                        "local",
                    ]
                    available_ids = _available_model_ids()
                    candidates = [
                        mid
                        for mid in preferred_order
                        if mid in available_ids and mid != selected_model
                    ]

                    # Record the initial upstream error
                    try:
                        monitoring_manager.log_error(
                            "adapter_error",
                            error or "Unknown adapter error",
                            {"client_ip": client_ip, "model": selected_model},
                            request_id=getattr(g, "request_id", None),
                        )
                    except Exception:
                        pass

                    for alt in candidates:
                        alt_adapter = get_adapter(alt)
                        if alt_adapter is None:
                            continue
                        alt_code, alt_err = alt_adapter.generate(composed_prompt)
                        if alt_err is None and alt_code:
                            # Log success under the fallback model
                            try:
                                monitoring_manager.log_request(
                                    model=alt,
                                    prompt_length=len(prompt),
                                    response_time=time.time() - start_time,
                                    success=True,
                                    client_ip=client_ip,
                                    error=None,
                                    request_id=getattr(g, "request_id", None),
                                )
                            except Exception:
                                pass
                            # Record assistant message to context on success
                            try:
                                context_manager.add_message(
                                    context_key, "assistant", alt_code
                                )
                            except Exception:
                                pass
                            return jsonify(
                                {
                                    "code": alt_code,
                                    "model_used": alt,
                                    "fallback_from": model,
                                }
                            )
                        else:
                            # Log each fallback attempt error for visibility
                            try:
                                monitoring_manager.log_error(
                                    "adapter_error",
                                    alt_err or "Unknown adapter error",
                                    {
                                        "client_ip": client_ip,
                                        "model": alt,
                                        "fallback_from": selected_model,
                                    },
                                    request_id=getattr(g, "request_id", None),
                                )
                            except Exception:
                                pass
            except Exception:
                # Never let fallback logic crash the route; proceed to standard error response
                pass

            # Upstream provider errors: return as clean JSON, 502/500
            status_code = (
                502
                if selected_model in {"openai", "huggingface", "anthropic", "gemini"}
                else 500
            )
            return _json_error(error, status_code)

        # Success: record assistant message to context
        try:
            context_manager.add_message(context_key, "assistant", code or "")
        except Exception:
            pass

        body: dict[str, Any] = {"code": code}
        # Include model_used when auto-selected or when debug requested
        if model == "auto" or debug:
            body["model_used"] = selected_model
        if router_info is not None:
            body["router"] = router_info
        # Include context inspection when debug is enabled
        if debug:
            try:
                info = context_manager.inspect(context_key)
                info["composed_chars"] = len(composed_prompt)
                body["context"] = info
            except Exception:
                pass
        return jsonify(body)

    except Exception as e:
        response_time = time.time() - start_time
        monitoring_manager.log_error(
            "unexpected_error",
            str(e),
            {"client_ip": client_ip},
            request_id=getattr(g, "request_id", None),
        )
        monitoring_manager.log_request(
            model="unknown",
            prompt_length=0,
            response_time=response_time,
            success=False,
            client_ip=client_ip,
            error=str(e),
            request_id=getattr(g, "request_id", None),
        )
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/generate-stream", methods=["POST"])
@limiter.limit(_generate_limit)
def generate_code_stream():
    start_time = time.time()
    # Harden client IP extraction: honor first XFF entry only
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

    try:
        data = request.get_json(silent=True)
        if data is None or not isinstance(data, dict):
            return _json_error("Invalid JSON payload", 400)

        prompt = data.get("prompt")
        model = data.get("model", "openai")
        debug = (
            _is_truthy(data.get("debug"))
            or _is_truthy(request.args.get("debug"))
            or _is_truthy(request.headers.get("X-Debug-Decision"))
        )

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

        sanitized_prompt = security_manager.sanitize_input(prompt)

        conv_id = (
            data.get("conversation_id")
            or data.get("conversationId")
            or request.headers.get("X-Conversation-Id")
        )
        user_id = getattr(g, "user_id", None)
        context_key = (conv_id or user_id or client_ip) or "unknown"
        context_manager.add_message(context_key, "user", sanitized_prompt)

        composed_prompt = context_manager.compose_prompt(context_key, sanitized_prompt)

        # Smart routing when model == "auto"
        router_info = None
        selected_model = model
        if model == "auto":
            available_ids = _available_model_ids()
            chosen, reason, ranked = _smart_route_model(sanitized_prompt, available_ids)
            selected_model = chosen
            if debug:
                router_info = {
                    "mode": "auto",
                    "chosen": chosen,
                    "reason": reason,
                    "candidates": ranked,
                    "available": available_ids,
                }

        adapter = get_adapter(selected_model)
        if adapter is None:
            return _json_error(f"Unknown model: {selected_model}", 400)

        code, error = adapter.generate(composed_prompt)

        response_time = time.time() - start_time
        monitoring_manager.log_request(
            model=selected_model,
            prompt_length=len(prompt),
            response_time=response_time,
            success=error is None,
            client_ip=client_ip,
            error=error,
            request_id=getattr(g, "request_id", None),
        )

        if error:
            # Attempt fallback to a backup model when enabled
            try:
                if bool(app.config.get("ENABLE_FALLBACK", True)):
                    preferred_order = [
                        "openai",
                        "anthropic",
                        "gemini",
                        "huggingface",
                        "local",
                    ]
                    available_ids = _available_model_ids()
                    candidates = [
                        mid for mid in preferred_order if mid in available_ids and mid != selected_model
                    ]

                    try:
                        monitoring_manager.log_error(
                            "adapter_error",
                            error or "Unknown adapter error",
                            {"client_ip": client_ip, "model": selected_model},
                            request_id=getattr(g, "request_id", None),
                        )
                    except Exception:
                        pass

                    for alt in candidates:
                        alt_adapter = get_adapter(alt)
                        if alt_adapter is None:
                            continue
                        alt_code, alt_err = alt_adapter.generate(composed_prompt)
                        if alt_err is None and alt_code:
                            try:
                                monitoring_manager.log_request(
                                    model=alt,
                                    prompt_length=len(prompt),
                                    response_time=time.time() - start_time,
                                    success=True,
                                    client_ip=client_ip,
                                    error=None,
                                    request_id=getattr(g, "request_id", None),
                                )
                            except Exception:
                                pass
                            try:
                                context_manager.add_message(context_key, "assistant", alt_code)
                            except Exception:
                                pass
                            code = alt_code
                            selected_model = alt
                            break
                        else:
                            try:
                                monitoring_manager.log_error(
                                    "adapter_error",
                                    alt_err or "Unknown adapter error",
                                    {"client_ip": client_ip, "model": alt, "fallback_from": selected_model},
                                    request_id=getattr(g, "request_id", None),
                                )
                            except Exception:
                                pass
            except Exception:
                pass

        if not code:
            status_code = (
                502
                if selected_model in {"openai", "huggingface", "anthropic", "gemini"}
                else 500
            )
            return _json_error(error or "No code generated", status_code)

        # Success: record assistant message to context
        try:
            context_manager.add_message(context_key, "assistant", code or "")
        except Exception:
            pass

        def _chunk_text(text: str, size: int = 512):
            for i in range(0, len(text), size):
                yield text[i : i + size]

        def _generate_stream():
            for chunk in _chunk_text(code):
                yield chunk

        return Response(stream_with_context(_generate_stream()), mimetype="text/plain")

    except Exception as e:
        response_time = time.time() - start_time
        monitoring_manager.log_error(
            "unexpected_error",
            str(e),
            {"client_ip": client_ip},
            request_id=getattr(g, "request_id", None),
        )
        monitoring_manager.log_request(
            model="unknown",
            prompt_length=0,
            response_time=response_time,
            success=False,
            client_ip=client_ip,
            error=str(e),
            request_id=getattr(g, "request_id", None),
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


## Metrics and security endpoints moved to metrics blueprint


def main():
    """GUI script entry point for running the Flask app."""
    app.run(debug=True)


if __name__ == "__main__":
    main()

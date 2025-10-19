import os
import time
from typing import Optional, Tuple, Dict, Any, List


import importlib.util
import sys
from typing import Callable
from dataclasses import dataclass


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


@dataclass
class AdapterRegistration:
    id: str
    name: str
    builder: Callable[[], "ModelAdapter"]
    is_available: Callable[[], bool]
    description: Optional[str] = None


_ADAPTER_REGISTRY: Dict[str, AdapterRegistration] = {}


def register_adapter(
    id: str,
    name: str,
    adapter_cls_or_factory: Callable[..., "ModelAdapter"],
    is_available: Optional[Callable[[], bool]] = None,
    description: Optional[str] = None,
) -> None:
    """Register a model adapter via plugin.

    - id: canonical model id (e.g., "mycloud", "mylocal")
    - name: human-friendly name
    - adapter_cls_or_factory: callable returning a ModelAdapter (class or factory)
    - is_available: function returning True when credentials/runtime are ready
    - description: optional text shown in docs or UI
    """

    def _builder() -> "ModelAdapter":
        return adapter_cls_or_factory()

    _ADAPTER_REGISTRY[id] = AdapterRegistration(
        id=id,
        name=name,
        builder=_builder,
        is_available=is_available or (lambda: True),
        description=description,
    )


def load_plugins(plugins_dir: Optional[str] = None) -> None:
    """Load plugin modules from a directory and invoke their register() function.

    Looks for Python files under `plugins_dir` (default: ./plugins/). Each module may
    optionally expose `register(register_adapter)` which receives the registration
    function to declare adapters.

    Never raises; startup should not fail due to plugin errors.
    """
    base_dir = plugins_dir or os.getenv("SCRIPT_AI_PLUGINS_DIR")
    if not base_dir:
        base_dir = os.path.join(os.path.dirname(__file__), "plugins")
    try:
        if not os.path.isdir(base_dir):
            return
        for fname in os.listdir(base_dir):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            path = os.path.join(base_dir, fname)
            mod_name = f"scriptai_plugin_{os.path.splitext(fname)[0]}"
            try:
                spec = importlib.util.spec_from_file_location(mod_name, path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = module
                    spec.loader.exec_module(module)
                    reg = getattr(module, "register", None)
                    if callable(reg):
                        reg(register_adapter)
            except Exception:
                # Skip broken plugin without interrupting startup
                pass
    except Exception:
        pass


class ModelAdapter:
    """Base adapter interface for model backends."""

    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        raise NotImplementedError


class OpenAIAdapter(ModelAdapter):
    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            import openai
        except Exception as e:  # pragma: no cover
            return None, f"OpenAI client import error: {str(e)}"

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
                request_timeout=30,
            )
            return response.choices[0].message.content, None
        except Exception as e:
            # Provide more robust, production-friendly error messages
            try:
                # Older OpenAI SDK exposes exceptions under openai.error
                if hasattr(openai, "error"):
                    if isinstance(
                        e, getattr(openai.error, "RateLimitError", Exception)
                    ):
                        return None, "OpenAI rate limit exceeded"
                    if isinstance(
                        e, getattr(openai.error, "AuthenticationError", Exception)
                    ):
                        return None, "Invalid OpenAI API key"
                    if isinstance(e, getattr(openai.error, "Timeout", Exception)):
                        return None, "OpenAI API timeout"
                    if isinstance(
                        e, getattr(openai.error, "APIConnectionError", Exception)
                    ):
                        return None, f"OpenAI API connection error: {str(e)}"
                    if isinstance(e, getattr(openai.error, "APIError", Exception)):
                        return None, f"OpenAI API error: {str(e)}"
            except Exception:
                # Fall back gracefully if introspection fails
                pass
            return None, f"Error with OpenAI API: {str(e)}"


class HuggingFaceAdapter(ModelAdapter):
    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            import requests
        except Exception as e:  # pragma: no cover
            return None, f"Requests import error: {str(e)}"

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
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    if "```" in generated_text:
                        code_parts = generated_text.split("```")
                        if len(code_parts) >= 2:
                            return code_parts[1].strip(), None
                    return generated_text.strip(), None
                return "No code generated", None
            else:
                # Provide friendlier error messages for common cases
                if response.status_code == 429:
                    return None, "HuggingFace rate limit exceeded"
                if 500 <= response.status_code < 600:
                    return None, f"HuggingFace service error ({response.status_code})"
                # Try to surface error details from JSON payload if present
                try:
                    err = response.json()
                    detail = err.get("error") if isinstance(err, dict) else None
                    if detail:
                        return None, f"HuggingFace API error: {detail}"
                except Exception:
                    pass
                return None, f"Error: API returned status code {response.status_code}"
        except Exception as e:
            return None, f"Error with HuggingFace API: {str(e)}"


class AnthropicAdapter(ModelAdapter):
    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            import anthropic
        except Exception as e:  # pragma: no cover
            return (
                None,
                f"Anthropic client import error: {str(e)}. Install with: pip install anthropic",
            )

        if not ANTHROPIC_API_KEY:
            return (
                None,
                (
                    "Anthropic API key not found. "
                    "Please set the ANTHROPIC_API_KEY environment variable."
                ),
            )

        try:
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            system_prompt = (
                "You are an expert programmer. Generate clean, efficient code "
                "with minimal explanation. Prefer returning only the code block."
            )
            resp = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1500,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            # Extract text from response
            try:
                # Claude responses are an array of content blocks
                text = "".join([getattr(b, "text", "") for b in resp.content])
            except Exception:
                text = str(resp)
            # Attempt to extract code block if present
            if "```" in text:
                parts = text.split("```")
                if len(parts) >= 2:
                    return parts[1].strip(), None
            return text.strip(), None
        except Exception as e:
            return None, f"Error with Anthropic API: {str(e)}"


class GeminiAdapter(ModelAdapter):
    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            import requests
        except Exception as e:  # pragma: no cover
            return None, f"Requests import error: {str(e)}"

        if not GOOGLE_API_KEY:
            return (
                None,
                (
                    "Google API key not found. "
                    "Please set the GOOGLE_API_KEY environment variable."
                ),
            )

        # Placeholder Gemini endpoint (for illustration)
        API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        full_prompt = f"Generate code for the following request: {prompt}\n\n```"
        try:
            response = requests.post(
                API_URL,
                params={"key": GOOGLE_API_KEY},
                json={"contents": [{"parts": [{"text": full_prompt}]}]},
                timeout=30,
            )
            if response.status_code == 200:
                data = response.json()
                # Simplified extraction
                text = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                if "```" in text:
                    parts = text.split("```")
                    if len(parts) >= 2:
                        return parts[1].strip(), None
                return text.strip(), None
            else:
                if response.status_code == 429:
                    return None, "Gemini rate limit exceeded"
                if 500 <= response.status_code < 600:
                    return None, f"Gemini service error ({response.status_code})"
                try:
                    err = response.json()
                    detail = err.get("error") if isinstance(err, dict) else None
                    if detail:
                        return None, f"Gemini API error: {detail}"
                except Exception:
                    pass
                return None, f"Error: API returned status code {response.status_code}"
        except Exception as e:
            return None, f"Error with Gemini API: {str(e)}"


def _detect_language(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in ["react", "component", "javascript", "node", "frontend"]):
        return "javascript"
    if any(k in p for k in ["sql", "database", "query", "postgres", "mysql"]):
        return "sql"
    if any(k in p for k in ["html", "css", "webpage", "template"]):
        return "html"
    return "python"


def _generate_stub(lang: str, prompt: str) -> str:
    if lang == "python":
        return (
            "# Generated locally based on prompt\n"
            f"# {prompt}\n"
            "def generated_function(*args, **kwargs):\n"
            "    \"\"\"\n"
            f"    Generated locally based on prompt: {prompt}\n"
            "    Replace this stub with your implementation.\n"
            "    \"\"\"\n"
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
    # Fallback to a simple Python stub
    return (
        "# Generated locally based on prompt\n"
        f"# {prompt}\n"
        "def generated_function():\n"
        "    pass\n"
    )


class LocalAdapter(ModelAdapter):
    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        lang = _detect_language(prompt)
        return _generate_stub(lang, prompt), None


def get_adapter(model: str) -> Optional[ModelAdapter]:
    # Prefer plugins/registry if present
    reg = _ADAPTER_REGISTRY.get(model)
    if reg:
        try:
            return reg.builder()
        except Exception:
            return None
    # Built-in adapters
    if model == "openai":
        return OpenAIAdapter()
    if model == "huggingface":
        return HuggingFaceAdapter()
    if model == "anthropic":
        return AnthropicAdapter()
    if model == "gemini":
        return GeminiAdapter()
    if model == "local":
        return LocalAdapter()
    return None


def available_models() -> List[Dict[str, Any]]:
    models = []
    if OPENAI_API_KEY:
        models.append({"id": "openai", "name": "OpenAI GPT-3.5"})
    if HUGGINGFACE_API_KEY:
        models.append({"id": "huggingface", "name": "HuggingFace StarCoder"})
    if ANTHROPIC_API_KEY:
        models.append({"id": "anthropic", "name": "Anthropic Claude"})
    if GOOGLE_API_KEY:
        models.append({"id": "gemini", "name": "Google Gemini"})
    models.append({"id": "local", "name": "Local Model (Placeholder)"})

    # Include registered plugin adapters that report availability
    try:
        for pid, reg in _ADAPTER_REGISTRY.items():
            if reg.is_available():
                if not any(m.get("id") == pid for m in models):
                    models.append({"id": pid, "name": reg.name})
    except Exception:
        pass

    return models

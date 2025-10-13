import os
import time
from typing import Optional, Tuple, Dict, Any, List


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")


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
            )
            return response.choices[0].message.content, None
        except Exception as e:
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
                return None, f"Error: API returned status code {response.status_code}"
        except Exception as e:
            return None, f"Error with HuggingFace API: {str(e)}"


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


class LocalAdapter(ModelAdapter):
    def generate(self, prompt: str) -> Tuple[Optional[str], Optional[str]]:
        lang = _detect_language(prompt)
        return _generate_stub(lang, prompt), None


def get_adapter(model: str) -> Optional[ModelAdapter]:
    if model == "openai":
        return OpenAIAdapter()
    if model == "huggingface":
        return HuggingFaceAdapter()
    if model == "local":
        return LocalAdapter()
    return None


def available_models() -> List[Dict[str, Any]]:
    models = []
    if OPENAI_API_KEY:
        models.append({"id": "openai", "name": "OpenAI GPT-3.5"})
    if HUGGINGFACE_API_KEY:
        models.append({"id": "huggingface", "name": "HuggingFace StarCoder"})
    models.append({"id": "local", "name": "Local Model (Placeholder)"})
    return models

# EOF
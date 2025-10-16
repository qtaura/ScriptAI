from __future__ import annotations

import os
from flask import Blueprint, jsonify

from model_adapters import available_models

bp = Blueprint("models", __name__)


@bp.route("/models")
def get_models():
    """Expose available models for the React UI."""
    return jsonify(available_models())


@bp.route("/model-profiles")
def get_model_profiles():
    """Expose dynamic model metadata for frontend display.

    Returns a JSON object with a "models" array. Each entry includes:
    - id, name
    - speed, quality, cost (categorical labels)
    - available (bool derived from environment)
    - badge, icon (UI hints)
    - features (short list of capabilities)
    """
    availability = {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "huggingface": bool(os.getenv("HUGGINGFACE_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "gemini": bool(os.getenv("GOOGLE_API_KEY")),
        "local": True,
    }

    models = [
        {
            "id": "openai",
            "name": "OpenAI GPT-3.5",
            "badge": "Recommended",
            "speed": "Fast",
            "quality": "High",
            "cost": "Paid",
            "icon": "Zap",
            "features": [
                "Production-ready code",
                "Complex algorithms",
                "Best error handling",
                "Extensive language support",
            ],
            "available": availability["openai"],
        },
        {
            "id": "anthropic",
            "name": "Anthropic Claude",
            "badge": "Reliable",
            "speed": "Fast",
            "quality": "High",
            "cost": "Paid",
            "icon": "Sparkles",
            "features": [
                "Strong reasoning",
                "Safe outputs",
                "Long context windows",
                "Great coding assistance",
            ],
            "available": availability["anthropic"],
        },
        {
            "id": "gemini",
            "name": "Google Gemini",
            "badge": "Powerful",
            "speed": "Fast",
            "quality": "High",
            "cost": "Paid",
            "icon": "Brain",
            "features": [
                "Multi-modal capabilities",
                "Strong reasoning",
                "Good code generation",
                "Google ecosystem integration",
            ],
            "available": availability["gemini"],
        },
        {
            "id": "huggingface",
            "name": "HuggingFace StarCoder",
            "badge": "Open Source",
            "speed": "Medium",
            "quality": "Good",
            "cost": "Free",
            "icon": "Clock",
            "features": [
                "Good for snippets",
                "Open source models",
                "No API costs",
            ],
            "available": availability["huggingface"],
        },
        {
            "id": "local",
            "name": "Local Model",
            "badge": "Privacy",
            "speed": "Slow",
            "quality": "Variable",
            "cost": "Free",
            "icon": "DollarSign",
            "features": [
                "Offline capability",
                "Complete privacy",
                "No API dependencies",
                "Customizable",
            ],
            "available": availability["local"],
        },
    ]

    # Preserve order but only include models configured in the system if desired.
    # For now, return all with availability flags so UI can indicate disabled ones.
    import time as _time

    return jsonify({"models": models, "timestamp": int(_time.time())})
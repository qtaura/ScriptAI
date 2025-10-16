"""
Prometheus client integration helpers.

This provides optional Prometheus exports without forcing the dependency
at import time in the main app module.
"""
from __future__ import annotations

from typing import Optional, Callable

try:  # pragma: no cover - import behavior tested via /metrics endpoint
    from prometheus_client import (
        generate_latest as _generate_latest,
        CONTENT_TYPE_LATEST as _CONTENT_TYPE_LATEST,
    )

    generate_latest: Optional[Callable[[], bytes]] = _generate_latest
    CONTENT_TYPE_LATEST: str = _CONTENT_TYPE_LATEST
except Exception:  # pragma: no cover
    generate_latest = None
    CONTENT_TYPE_LATEST = "text/plain; charset=utf-8"


__all__ = ["generate_latest", "CONTENT_TYPE_LATEST"]

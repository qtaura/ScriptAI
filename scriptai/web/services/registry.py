from __future__ import annotations

"""
Service registry for application-wide singletons.

Exposes initialized instances for monitoring and security that can be
imported by route blueprints and the app factory without circular imports.
"""

from monitoring import MonitoringManager
from security import SecurityManager
from scriptai.web.services.context import ContextManager

# Initialize shared service instances
security_manager = SecurityManager()
monitoring_manager = MonitoringManager()
context_manager = ContextManager()

__all__ = ["security_manager", "monitoring_manager", "context_manager"]

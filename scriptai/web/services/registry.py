from __future__ import annotations

"""
Service registry for application-wide singletons.

Exposes initialized instances for monitoring and security that can be
imported by route blueprints and the app factory without circular imports.
"""

from monitoring import MonitoringManager
from security import SecurityManager

# Initialize shared service instances
security_manager = SecurityManager()
monitoring_manager = MonitoringManager()

__all__ = ["security_manager", "monitoring_manager"]
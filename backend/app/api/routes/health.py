"""
Health API Route
Provides service liveness and runtime status probes.
"""

from backend.app.api.v1.endpoints.health import router

__all__ = ["router"]

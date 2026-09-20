"""
Bloop V1 API Router (Compatibility Forwarder)
Directs requests to the centralized api_router in backend.app.api.router.
"""

from backend.app.api.router import api_router

__all__ = ["api_router"]

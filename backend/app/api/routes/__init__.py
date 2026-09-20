"""
Bloop API Routes Module
Exports the centralized API router and route handlers for FastAPI.
"""

from backend.app.api.router import api_router
from backend.app.api.v1.endpoints import (
    auth,
    favorites,
    health,
    history,
    languages,
    quantum,
    tts,
    users,
    voices,
)

__all__ = [
    "api_router",
    "health",
    "auth",
    "users",
    "languages",
    "voices",
    "tts",
    "history",
    "favorites",
    "quantum",
]

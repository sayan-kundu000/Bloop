"""
Bloop Central API Router
Composes all 9 domain routers under a unified, versioned API structure.
"""

from fastapi import APIRouter
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

api_router = APIRouter()

# Domain Router Registrations
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(languages.router, prefix="/languages", tags=["Languages"])
api_router.include_router(voices.router, prefix="/voices", tags=["Voices"])
api_router.include_router(tts.router, prefix="/tts", tags=["Speech"])
api_router.include_router(history.router, prefix="/history", tags=["History"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
api_router.include_router(quantum.router, prefix="/quantum", tags=["Quantum"])

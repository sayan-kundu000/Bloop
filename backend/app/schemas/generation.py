"""
Bloop Generation Schemas (Compatibility Module)
Forwarding definitions to backend.app.schemas.history and backend.app.schemas.favorite.
"""

from backend.app.schemas.history import GenerationResponse, HistoryItemResponse
from backend.app.schemas.favorite import FavoriteCreate, FavoriteResponse

__all__ = [
    "GenerationResponse",
    "HistoryItemResponse",
    "FavoriteCreate",
    "FavoriteResponse",
]

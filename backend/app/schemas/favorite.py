"""
Bloop Favorite Domain Schemas
Defines request and response schemas for bookmarking speech generation outputs.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.schemas.history import HistoryItemResponse


class FavoriteCreate(BaseModel):
    """Request payload to bookmark a speech generation record."""
    generation_id: int = Field(..., ge=1, description="Target generation record ID to favorite")
    label: Optional[str] = Field(None, max_length=100, description="Optional custom bookmark label or note")


class FavoriteResponse(BaseModel):
    """Detailed response schema for a favorited speech generation record."""
    id: int = Field(..., description="Unique favorite record identifier")
    user_id: int = Field(..., description="Owner user ID")
    generation_id: int = Field(..., description="Target speech generation ID")
    label: Optional[str] = Field(None, description="Custom bookmark label")
    created_at: datetime = Field(..., description="Timestamp of bookmark creation")
    generation: Optional[HistoryItemResponse] = Field(None, description="Embedded speech generation details")

    class Config:
        from_attributes = True


class FavoriteDeleteResponse(BaseModel):
    """Response confirming bookmark deletion."""
    deleted_id: int = Field(..., description="Identifier of the deleted favorite record")
    message: str = Field("Removed from favorites.", description="Confirmation message")

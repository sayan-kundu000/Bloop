"""
Bloop History Domain Schemas
Defines request and response schemas for speech generation audit trails,
filtering, search, sorting, and pagination.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class HistoryItemResponse(BaseModel):
    """Detailed response schema for a single speech generation record."""
    id: int = Field(..., description="Unique generation record identifier")
    user_id: Optional[int] = Field(None, description="Owning user ID if authenticated")
    text: str = Field(..., description="Synthesized text content")
    char_count: int = Field(..., description="Total character length")
    word_count: int = Field(..., description="Total word count")
    language_code: str = Field(..., description="BCP-47 language locale (e.g. en-US)")
    voice_id: str = Field(..., description="Voice identifier used for synthesis")
    voice_name: Optional[str] = Field(None, description="Human-readable voice display name")
    status: str = Field("completed", description="Lifecycle state: pending, processing, completed, failed")
    audio_url: Optional[str] = Field(None, description="Relative URL to stream audio with HTTP Range support")
    download_url: Optional[str] = Field(None, description="Direct download URL with attachment header")
    duration_seconds: float = Field(0.0, description="Audio playback duration in seconds")
    file_size_bytes: int = Field(0, description="Audio file size in bytes")
    provider: str = Field("elevenlabs", description="TTS synthesis provider")
    is_favorite: bool = Field(False, description="Whether the requesting user has bookmarked this record")
    favorite_id: Optional[int] = Field(None, description="Favorite record ID if bookmarked")
    created_at: datetime = Field(..., description="Timestamp of generation creation")

    class Config:
        from_attributes = True


# Backward compatibility alias
GenerationResponse = HistoryItemResponse


class HistoryQueryFilter(BaseModel):
    """Query parameter filter for history retrieval."""
    search: Optional[str] = Field(None, max_length=100, description="Keyword search across text and voice name")
    language: Optional[str] = Field(None, max_length=10, description="Filter by language code")
    status: Optional[str] = Field(None, pattern="^(completed|failed|pending|processing)$", description="Filter by generation lifecycle status")
    favorite: Optional[bool] = Field(None, description="Filter only favorited generations if true, non-favorited if false")
    created_after: Optional[datetime] = Field(None, description="Filter generations created on or after this timestamp")
    created_before: Optional[datetime] = Field(None, description="Filter generations created on or before this timestamp")
    sort_by: str = Field("created_at", pattern="^(created_at|duration_seconds|char_count|word_count)$", description="Sort attribute")
    order: str = Field("desc", pattern="^(asc|desc)$", description="Sort direction")
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


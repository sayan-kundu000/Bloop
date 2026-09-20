"""
Speech Service Internal Data Transfer Objects (DTOs)
Decouples API request/response schemas from internal speech orchestration logic.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class SpeechRequestDTO(BaseModel):
    """Internal DTO representing a speech synthesis request."""
    text: str
    voice_id: str
    language: str = "en-US"
    speed: Optional[float] = 1.0
    pitch: Optional[float] = 1.0
    emotion: Optional[str] = "Neutral"
    settings: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None
    request_id: Optional[str] = None


class SpeechResultDTO(BaseModel):
    """Internal DTO representing the outcome of speech orchestration."""
    generation_id: Optional[int] = None
    audio_filename: str
    audio_url: str
    download_url: str
    text: str
    char_count: int
    word_count: int
    language: str
    voice_id: str
    voice_name: Optional[str] = None
    duration_seconds: float = 0.0
    file_size_bytes: int = 0
    provider: str
    provider_request_id: Optional[str] = None
    is_simulation: bool = False
    emotion: Optional[str] = None
    quantum_metrics: Optional[Any] = None

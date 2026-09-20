"""
TTS Provider Type Definitions
Defines request parameters, audio format options, and provider synthesis results.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class TTSGenerationOptions(BaseModel):
    language: Optional[str] = "en-US"
    speed: Optional[float] = Field(default=1.0, ge=0.5, le=2.0)
    pitch: Optional[float] = Field(default=1.0, ge=0.5, le=2.0)
    emotion: Optional[str] = "neutral"
    pitch_override: Optional[str] = None
    rate_override: Optional[str] = None
    audio_format: Optional[str] = "mp3"


class ProviderSpeechResult(BaseModel):
    audio_bytes: bytes
    format: str = "mp3"
    duration_seconds: float = 0.0
    provider: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

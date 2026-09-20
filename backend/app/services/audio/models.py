"""
Audio Domain Models & Value Objects
Defines internal data representations for raw audio inspection, validation,
content type resolution, and delivery metadata.
"""

from typing import Optional
from pydantic import BaseModel, Field


class AudioMetadata(BaseModel):
    """Normalized technical and acoustic metadata for generated audio payloads."""
    content_type: str = Field("audio/mpeg", description="MIME content type (e.g. audio/mpeg, audio/wav)")
    audio_format: str = Field("mp3", description="Audio format container name (mp3, wav, ogg)")
    file_extension: str = Field("mp3", description="Canonical file extension without dot")
    file_size_bytes: int = Field(0, ge=0, description="Total byte size of audio content")
    duration_seconds: Optional[float] = Field(None, ge=0.0, description="Calculated or estimated duration in seconds")
    bitrate_kbps: Optional[int] = Field(None, description="Audio bitrate in kbps if extractable")
    sample_rate_hz: Optional[int] = Field(None, description="Sampling rate in Hz (e.g. 44100, 24000)")
    channels: Optional[int] = Field(None, description="Number of audio channels (1 for mono, 2 for stereo)")


class AudioValidationResult(BaseModel):
    """Evaluation result from raw audio byte stream inspection."""
    is_valid: bool = Field(..., description="Whether the audio payload passed structure and safety checks")
    detected_format: Optional[str] = Field(None, description="Format detected from magic bytes (mp3, wav, ogg)")
    detected_mime_type: Optional[str] = Field(None, description="MIME type derived from magic headers")
    file_size_bytes: int = Field(0, description="Validated payload length in bytes")
    error_message: Optional[str] = Field(None, description="Description of validation failure if invalid")


class ProcessedAudio(BaseModel):
    """Validated, normalized audio payload ready for storage and controlled delivery."""
    audio_bytes: bytes = Field(..., description="Raw sanitized audio byte content")
    metadata: AudioMetadata = Field(..., description="Extracted delivery and catalog metadata")

    class Config:
        arbitrary_types_allowed = True

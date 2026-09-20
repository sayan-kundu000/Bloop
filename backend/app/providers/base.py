"""
Bloop TTS Provider Base Contract & Result Abstraction
Defines the abstract interface for all speech synthesis providers and
a normalized provider result representation decoupled from third-party vendor SDKs.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class TTSProviderResult(BaseModel):
    """
    Normalized speech generation result returned by TTS provider adapters.
    Isolates external vendor API payload structures from internal Bloop domain models.
    """
    audio_bytes: bytes
    content_type: str = "audio/mpeg"
    file_extension: str = "mp3"
    provider: str = "elevenlabs"
    provider_request_id: Optional[str] = None
    duration_seconds: Optional[float] = None
    latency_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class TTSProvider(ABC):
    """Abstract interface for all Text-to-Speech provider adapters."""

    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        language_code: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Union[TTSProviderResult, bytes]:
        """
        Generate speech audio and return normalized provider result or raw audio bytes.
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider identifier name."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider credentials/configuration are active."""
        pass

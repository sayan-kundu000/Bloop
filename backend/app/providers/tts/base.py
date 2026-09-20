"""
Base Text-to-Speech Provider Interface
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class TTSProvider(ABC):
    """Abstract interface for all Text-to-Speech provider adapters."""

    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate raw audio bytes for the given text and voice configuration."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider identifier name."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider credentials/configuration are active."""
        pass

"""
Legacy ElevenLabs Provider Re-export
Maintains backward-compatibility for direct module imports.
"""

from backend.app.providers.elevenlabs.provider import ElevenLabsProvider
from backend.app.providers.elevenlabs.exceptions import (
    ElevenLabsException,
    ElevenLabsAuthenticationException,
    ElevenLabsRateLimitException,
    ElevenLabsTimeoutException,
    ElevenLabsUnavailableException,
    ElevenLabsValidationException,
    ElevenLabsVoiceNotFoundException,
)

__all__ = [
    "ElevenLabsProvider",
    "ElevenLabsException",
    "ElevenLabsAuthenticationException",
    "ElevenLabsRateLimitException",
    "ElevenLabsTimeoutException",
    "ElevenLabsUnavailableException",
    "ElevenLabsValidationException",
    "ElevenLabsVoiceNotFoundException",
]

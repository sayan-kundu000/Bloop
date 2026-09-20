"""
ElevenLabs Provider Subsystem
Exposes client, adapter, mapper, and domain exceptions for ElevenLabs speech synthesis.
"""

from backend.app.providers.elevenlabs.client import ElevenLabsClient
from backend.app.providers.elevenlabs.exceptions import (
    ElevenLabsAuthenticationException,
    ElevenLabsException,
    ElevenLabsRateLimitException,
    ElevenLabsTimeoutException,
    ElevenLabsUnavailableException,
    ElevenLabsValidationException,
    ElevenLabsVoiceNotFoundException,
)
from backend.app.providers.elevenlabs.mapper import ElevenLabsSettingsMapper
from backend.app.providers.elevenlabs.provider import ElevenLabsProvider

__all__ = [
    "ElevenLabsClient",
    "ElevenLabsProvider",
    "ElevenLabsSettingsMapper",
    "ElevenLabsException",
    "ElevenLabsAuthenticationException",
    "ElevenLabsRateLimitException",
    "ElevenLabsTimeoutException",
    "ElevenLabsUnavailableException",
    "ElevenLabsValidationException",
    "ElevenLabsVoiceNotFoundException",
]

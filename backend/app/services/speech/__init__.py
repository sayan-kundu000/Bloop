"""
Bloop Speech Service Subsystem
Exposes SpeechService, request/result DTOs, and domain speech exceptions.
"""

from backend.app.services.speech.exceptions import (
    ProviderNotConfiguredException,
    SpeechPersistenceException,
    SpeechServiceException,
)
from backend.app.services.speech.models import SpeechRequestDTO, SpeechResultDTO
from backend.app.services.speech.service import SpeechService

__all__ = [
    "SpeechService",
    "SpeechRequestDTO",
    "SpeechResultDTO",
    "SpeechServiceException",
    "ProviderNotConfiguredException",
    "SpeechPersistenceException",
]

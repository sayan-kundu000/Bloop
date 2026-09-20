"""
Audio Domain Exceptions
Defines and re-exports exceptions for the audio processing and delivery subsystem.
"""

from backend.app.core.exceptions import (
    AudioDeliveryException,
    AudioGenerationInvalidException,
    AudioNotFoundException,
    BloopException,
    ErrorCode,
    GenerationAccessDeniedException,
    GenerationNotFoundException,
)


class AudioProcessingException(BloopException):
    """Base exception for all audio processing domain errors."""

    def __init__(
        self,
        message: str = "Audio processing failed.",
        code: str = ErrorCode.AUDIO_GENERATION_INVALID,
        status_code: int = 422,
        details: dict = None,
    ):
        super().__init__(message=message, code=code, status_code=status_code, details=details)


__all__ = [
    "AudioProcessingException",
    "AudioGenerationInvalidException",
    "AudioNotFoundException",
    "GenerationNotFoundException",
    "GenerationAccessDeniedException",
    "AudioDeliveryException",
]

"""
Speech Service Exceptions
Domain exceptions raised during speech orchestration lifecycle.
"""

from typing import Any, Dict, Optional
from fastapi import status
from backend.app.core.exceptions import BloopException, ErrorCode


class SpeechServiceException(BloopException):
    """Base exception for speech service orchestration errors."""

    def __init__(
        self,
        message: str = "Speech service encountered an error.",
        code: str = ErrorCode.TTS_GENERATION_FAILED,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class ProviderNotConfiguredException(SpeechServiceException):
    """Raised when the selected TTS provider lacks required credentials or environment configuration."""

    def __init__(
        self,
        provider: str = "elevenlabs",
        message: Optional[str] = None,
    ):
        super().__init__(
            message=message or f"TTS Provider '{provider}' is not configured in this environment.",
            code=ErrorCode.TTS_PROVIDER_UNAVAILABLE,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"provider": provider},
        )


class SpeechPersistenceException(SpeechServiceException):
    """Raised when generation metadata cannot be safely persisted to the database."""

    def __init__(
        self,
        message: str = "Failed to record generation metadata in database.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.DATABASE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )

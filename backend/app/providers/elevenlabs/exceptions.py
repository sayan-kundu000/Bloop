"""
ElevenLabs Provider Exception Hierarchy
Defines domain exceptions for ElevenLabs API errors, translating third-party
failure modes into standardized Bloop error envelopes without credential leakage.
"""

from typing import Any, Dict, Optional
from fastapi import status
from backend.app.core.exceptions import BloopException, ErrorCode


class ElevenLabsException(BloopException):
    """Base exception for all ElevenLabs provider communication failures."""

    def __init__(
        self,
        message: str = "ElevenLabs TTS provider encountered an error.",
        code: str = ErrorCode.PROVIDER_ERROR,
        status_code: int = status.HTTP_502_BAD_GATEWAY,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            details=details or {"provider": "elevenlabs"},
        )


class ElevenLabsAuthenticationException(ElevenLabsException):
    """
    Raised when ElevenLabs returns HTTP 401 Unauthorized or API key is unconfigured.
    Guarantees API keys are never included in error messages or exception details.
    """

    def __init__(
        self,
        message: str = "Speech generation provider authentication failed. Check backend configuration.",
        details: Optional[Dict[str, Any]] = None,
    ):
        clean_details = details or {}
        # Ensure no accidental key leaks in details
        clean_details.pop("api_key", None)
        clean_details["provider"] = "elevenlabs"
        super().__init__(
            message=message,
            code=ErrorCode.TTS_PROVIDER_UNAVAILABLE,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=clean_details,
        )


class ElevenLabsRateLimitException(ElevenLabsException):
    """Raised when ElevenLabs quota is exhausted or rate limit is triggered (HTTP 429)."""

    def __init__(
        self,
        message: str = "Speech generation service quota exceeded or rate limit reached. Please try again later.",
        retry_after_seconds: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        det = details or {"provider": "elevenlabs"}
        if retry_after_seconds is not None:
            det["retry_after_seconds"] = retry_after_seconds
        super().__init__(
            message=message,
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=det,
        )


class ElevenLabsVoiceNotFoundException(ElevenLabsException):
    """Raised when the requested voice ID is not recognized by ElevenLabs (HTTP 404)."""

    def __init__(
        self,
        voice_id: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        det = details or {"provider": "elevenlabs", "voice_id": voice_id}
        super().__init__(
            message=message or f"The selected voice '{voice_id}' is not available on ElevenLabs.",
            code=ErrorCode.INVALID_VOICE,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=det,
        )


class ElevenLabsValidationException(ElevenLabsException):
    """Raised when request parameters fail ElevenLabs payload schema validation (HTTP 400/422)."""

    def __init__(
        self,
        message: str = "Invalid settings or payload for ElevenLabs speech generation.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details or {"provider": "elevenlabs"},
        )


class ElevenLabsUnavailableException(ElevenLabsException):
    """Raised when ElevenLabs API is down, network drops, or gateway errors occur (HTTP 502/503/504)."""

    def __init__(
        self,
        message: str = "Speech generation service is temporarily unavailable. Please try again shortly.",
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code=ErrorCode.TTS_PROVIDER_UNAVAILABLE,
            status_code=status_code,
            details=details or {"provider": "elevenlabs"},
        )


class ElevenLabsTimeoutException(ElevenLabsUnavailableException):
    """Raised when ElevenLabs fails to respond within the configured connection or read timeout."""

    def __init__(
        self,
        message: str = "ElevenLabs TTS service timed out while synthesizing audio.",
        timeout_seconds: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        det = details or {"provider": "elevenlabs"}
        if timeout_seconds is not None:
            det["timeout_seconds"] = timeout_seconds
        super().__init__(
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            details=det,
        )

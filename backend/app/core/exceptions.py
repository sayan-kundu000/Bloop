"""
Bloop Core Exceptions & Error Handling System
Defines the application-wide custom domain exception hierarchy,
standardized machine-readable error codes, and JSON exception handlers.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.logging import logger


class ErrorCode:
    """Standardized API machine-readable error codes (Prompt 09 §9)."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCESS_DENIED = "ACCESS_DENIED"
    FORBIDDEN = "FORBIDDEN"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    CONFLICT = "CONFLICT"
    INVALID_LANGUAGE = "INVALID_LANGUAGE"
    INVALID_VOICE = "INVALID_VOICE"
    VOICE_LANGUAGE_MISMATCH = "VOICE_LANGUAGE_MISMATCH"
    TEXT_EMPTY = "TEXT_EMPTY"
    TEXT_TOO_LONG = "TEXT_TOO_LONG"
    TTS_GENERATION_FAILED = "TTS_GENERATION_FAILED"
    AUDIO_GENERATION_FAILED = "AUDIO_GENERATION_FAILED"
    TTS_PROVIDER_UNAVAILABLE = "TTS_PROVIDER_UNAVAILABLE"
    TTS_PROVIDER_RATE_LIMITED = "TTS_PROVIDER_RATE_LIMITED"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUANTUM_DISABLED = "QUANTUM_DISABLED"
    QUANTUM_UNAVAILABLE = "QUANTUM_UNAVAILABLE"
    INVALID_QUANTUM_REQUEST = "INVALID_QUANTUM_REQUEST"
    INVALID_QUBIT_COUNT = "INVALID_QUBIT_COUNT"
    QUBIT_LIMIT_EXCEEDED = "QUBIT_LIMIT_EXCEEDED"
    INVALID_SHOTS = "INVALID_SHOTS"
    SHOT_LIMIT_EXCEEDED = "SHOT_LIMIT_EXCEEDED"
    QUANTUM_EXECUTION_FAILED = "QUANTUM_EXECUTION_FAILED"
    QUANTUM_EXECUTION_TIMEOUT = "QUANTUM_EXECUTION_TIMEOUT"
    UNSUPPORTED_FRAMEWORK = "UNSUPPORTED_FRAMEWORK"
    UNSUPPORTED_EXPERIMENT = "UNSUPPORTED_EXPERIMENT"
    QUANTUM_RESOURCE_LIMIT = "QUANTUM_RESOURCE_LIMIT"
    HYBRID_EXECUTION_FAILED = "HYBRID_EXECUTION_FAILED"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    AUDIO_GENERATION_INVALID = "AUDIO_GENERATION_INVALID"
    AUDIO_NOT_FOUND = "AUDIO_NOT_FOUND"
    GENERATION_NOT_FOUND = "GENERATION_NOT_FOUND"
    GENERATION_ACCESS_DENIED = "GENERATION_ACCESS_DENIED"
    AUDIO_DELIVERY_FAILED = "AUDIO_DELIVERY_FAILED"
    DOWNLOAD_UNAVAILABLE = "DOWNLOAD_UNAVAILABLE"


class BloopException(Exception):
    """Base exception for all Bloop platform domain errors."""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.INTERNAL_SERVER_ERROR,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ValidationException(BloopException):
    """Raised when request payload or domain rule validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, code: str = ErrorCode.VALIDATION_ERROR):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


ValidationError = ValidationException  # Backward-compatibility alias


class TextEmptyException(ValidationException):
    """Raised when submitted text is empty or solely whitespace."""

    def __init__(self, message: str = "Text cannot be empty", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.TEXT_EMPTY,
            details=details or {"reason": "empty_or_whitespace_only"},
        )


class TextTooLongException(ValidationException):
    """Raised when submitted text exceeds the maximum allowable character limit."""

    def __init__(
        self,
        message: str = "Text exceeds the maximum allowed length",
        max_characters: Optional[int] = None,
        actual_characters: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        det = details or {}
        if max_characters is not None:
            det["max_characters"] = max_characters
        if actual_characters is not None:
            det["actual_characters"] = actual_characters
        super().__init__(
            message=message,
            code=ErrorCode.TEXT_TOO_LONG,
            details=det,
        )


class InvalidLanguageException(ValidationException):
    """Raised when the requested language is not supported or not enabled (Prompt 11 §26)."""

    def __init__(
        self,
        message: str = "The selected language is not available",
        language_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        det = details or {}
        if language_code is not None:
            det["language_code"] = language_code
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_LANGUAGE,
            details=det,
        )


class InvalidVoiceException(ValidationException):
    """Raised when the requested voice is not found or not enabled (Prompt 11 §27)."""

    def __init__(
        self,
        message: str = "The selected voice is not available",
        voice_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        det = details or {}
        if voice_id is not None:
            det["voice_id"] = voice_id
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_VOICE,
            details=det,
        )


class VoiceLanguageMismatchException(ValidationException):
    """Raised when a voice does not support the requested language locale (Prompt 11 §28)."""

    def __init__(
        self,
        message: Optional[str] = None,
        voice_id: Optional[str] = None,
        language_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        det = details or {}
        if voice_id is not None:
            det["voice_id"] = voice_id
        if language_code is not None:
            det["language_code"] = language_code
        msg = message or f"Voice '{voice_id or 'unknown'}' does not support language '{language_code or 'unknown'}'"
        super().__init__(
            message=msg,
            code=ErrorCode.VOICE_LANGUAGE_MISMATCH,
            details=det,
        )


class AuthenticationException(BloopException):
    """Raised when user credentials are invalid, missing, or expired."""

    def __init__(self, message: str = "Authentication required", code: str = ErrorCode.AUTHENTICATION_FAILED):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


AuthenticationError = AuthenticationException  # Backward-compatibility alias


class AuthorizationException(BloopException):
    """Raised when user lacks permission to access a requested resource."""

    def __init__(self, message: str = "Access denied", code: str = ErrorCode.FORBIDDEN):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_403_FORBIDDEN,
        )


AuthorizationError = AuthorizationException  # Backward-compatibility alias


class ResourceNotFoundException(BloopException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            code=ErrorCode.RESOURCE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)},
        )


NotFoundError = ResourceNotFoundException  # Backward-compatibility alias


class ConflictException(BloopException):
    """Raised when an entity violates uniqueness or a conflicting state exists."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, code: str = ErrorCode.CONFLICT):
        super().__init__(
            message=message,
            code=code,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class RateLimitException(BloopException):
    """Raised when a user or IP exceeds the allowable request quota."""

    def __init__(self, message: str = "Too many requests. Please try again later.", retry_after: int = 60):
        super().__init__(
            message=message,
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after_seconds": retry_after},
        )


RateLimitError = RateLimitException  # Backward-compatibility alias


class ProviderException(BloopException):
    """Raised when an external service or provider (e.g., ElevenLabs) fails."""

    def __init__(self, provider: str, message: str, details: Optional[Dict[str, Any]] = None, code: str = ErrorCode.PROVIDER_ERROR):
        super().__init__(
            message=f"Provider '{provider}' error: {message}",
            code=code,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details or {"provider": provider},
        )


ProviderError = ProviderException  # Backward-compatibility alias


class DatabaseException(BloopException):
    """Raised when an internal persistence or query operation fails."""

    def __init__(self, message: str = "A database error occurred", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.DATABASE_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class ServiceUnavailableException(BloopException):
    """Raised when a required external or internal subsystem is currently unavailable."""

    def __init__(self, service: str, message: Optional[str] = None, code: str = ErrorCode.SERVICE_UNAVAILABLE):
        super().__init__(
            message=message or f"Service '{service}' is temporarily unavailable",
            code=code,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service": service},
        )


class QuantumDisabledException(BloopException):
    """Raised when an endpoint requires Quantum Intelligence but QUANTUM_ENABLED=false."""

    def __init__(self, message: str = "Quantum intelligence subsystem is disabled in this environment."):
        super().__init__(
            message=message,
            code=ErrorCode.QUANTUM_DISABLED,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"subsystem": "quantum"},
        )


class QuantumUnavailableException(BloopException):
    """Raised when quantum framework libraries or execution devices are unavailable."""

    def __init__(self, message: str = "Quantum execution runtime is currently unavailable.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.QUANTUM_UNAVAILABLE,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details or {"subsystem": "quantum"},
        )


class InvalidQuantumRequestException(ValidationException):
    """Raised when quantum parameters, gates, or configurations are invalid."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_QUANTUM_REQUEST,
            details=details,
        )


class QubitLimitExceededException(ValidationException):
    """Raised when requested qubits exceed QUANTUM_MAX_QUBITS."""

    def __init__(self, message: str, max_qubits: int, requested_qubits: int):
        super().__init__(
            message=message,
            code=ErrorCode.QUBIT_LIMIT_EXCEEDED,
            details={"max_qubits": max_qubits, "requested_qubits": requested_qubits},
        )


class ShotLimitExceededException(ValidationException):
    """Raised when requested shots exceed QUANTUM_MAX_SHOTS."""

    def __init__(self, message: str, max_shots: int, requested_shots: int):
        super().__init__(
            message=message,
            code=ErrorCode.SHOT_LIMIT_EXCEEDED,
            details={"max_shots": max_shots, "requested_shots": requested_shots},
        )


class QuantumExecutionTimeoutException(BloopException):
    """Raised when quantum simulation exceeds allowable execution window."""

    def __init__(self, message: str = "Quantum simulation exceeded execution timeout limit.", timeout_seconds: Optional[float] = None):
        super().__init__(
            message=message,
            code=ErrorCode.QUANTUM_EXECUTION_TIMEOUT,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            details={"timeout_seconds": timeout_seconds} if timeout_seconds else {},
        )


class UnsupportedFrameworkException(ValidationException):
    """Raised when an unknown or unconfigured quantum framework is requested."""

    def __init__(self, framework: str, supported: Optional[List[str]] = None):
        supp = supported or ["qiskit", "pennylane", "hybrid"]
        super().__init__(
            message=f"Unsupported quantum framework '{framework}'. Supported: {', '.join(supp)}",
            code=ErrorCode.UNSUPPORTED_FRAMEWORK,
            details={"framework": framework, "supported_frameworks": supp},
        )


class UnsupportedExperimentException(ValidationException):
    """Raised when an unknown experiment type is requested."""

    def __init__(self, experiment_type: str, supported: Optional[List[str]] = None):
        supp = supported or ["basic_circuit", "quantum_text", "quantum_emotion", "quantum_semantic", "hybrid_ml", "benchmark"]
        super().__init__(
            message=f"Unsupported quantum experiment '{experiment_type}'. Supported: {', '.join(supp)}",
            code=ErrorCode.UNSUPPORTED_EXPERIMENT,
            details={"experiment_type": experiment_type, "supported_experiments": supp},
        )


class HybridExecutionFailedException(BloopException):
    """Raised when hybrid quantum-classical ML pipeline execution fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Hybrid ML execution failure: {message}",
            code=ErrorCode.HYBRID_EXECUTION_FAILED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class QuantumExecutionError(BloopException):
    """Raised when Qiskit or PennyLane simulation / execution fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Quantum execution failure: {message}",
            code=ErrorCode.QUANTUM_EXECUTION_FAILED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )



class ConfigurationError(BloopException):
    """Raised when a mandatory environment variable or system configuration is missing."""

    def __init__(self, key: str, message: Optional[str] = None):
        super().__init__(
            message=message or f"Required configuration '{key}' is missing or invalid",
            code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"config_key": key},
        )


class AudioGenerationFailedException(BloopException):
    """Raised when audio synthesis fails at provider or execution layer (Prompt 13 §37)."""

    def __init__(self, message: str = "Audio speech generation failed.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.AUDIO_GENERATION_FAILED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class AudioGenerationInvalidException(BloopException):
    """Raised when generated audio payload is empty, corrupt, or invalid (Prompt 13 §11)."""

    def __init__(self, message: str = "Generated audio payload is invalid or corrupted.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.AUDIO_GENERATION_INVALID,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class AudioNotFoundException(ResourceNotFoundException):
    """Raised when the requested physical audio file is missing from server storage (Prompt 13 §40)."""

    def __init__(self, identifier: Any, message: Optional[str] = None):
        super().__init__(
            resource="AudioFile",
            identifier=identifier,
        )
        self.code = ErrorCode.AUDIO_NOT_FOUND
        if message:
            self.message = message


class GenerationNotFoundException(ResourceNotFoundException):
    """Raised when a requested speech generation record is not found in database."""

    def __init__(self, identifier: Any, message: Optional[str] = None):
        super().__init__(
            resource="SpeechGeneration",
            identifier=identifier,
        )
        self.code = ErrorCode.GENERATION_NOT_FOUND
        if message:
            self.message = message


class GenerationAccessDeniedException(AuthorizationException):
    """Raised when a user attempts to access audio belonging to another user (Prompt 13 §18)."""

    def __init__(self, generation_id: Any, message: Optional[str] = None):
        super().__init__(
            message=message or "Access denied. You do not have permission to access this speech generation.",
            code=ErrorCode.GENERATION_ACCESS_DENIED,
        )
        self.status_code = status.HTTP_403_FORBIDDEN
        self.details = {"generation_id": str(generation_id)}


class AudioDeliveryException(BloopException):
    """Raised when an unexpected error occurs while delivering or streaming audio."""

    def __init__(self, message: str = "Audio delivery failed. Please try again.", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.AUDIO_DELIVERY_FAILED,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


# ============================================================================
# Centralized FastAPI Exception Handlers
# ============================================================================

async def bloop_exception_handler(request: Request, exc: BloopException) -> JSONResponse:
    """Handles all Bloop custom domain exceptions using the standard error contract."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handles FastAPI and Starlette HTTP exceptions with uniform formatting."""
    detail = exc.detail
    details = {}
    if isinstance(detail, dict):
        code = detail.get("code", f"HTTP_{exc.status_code}")
        message = detail.get("message", str(detail))
        details = detail.get("details", {})
    else:
        code = f"HTTP_{exc.status_code}"
        message = str(detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handles Pydantic request payload validation errors cleanly."""
    errors = exc.errors()
    first_msg = errors[0]["msg"] if errors else "Validation error"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.VALIDATION_ERROR,
                "message": first_msg,
                "details": jsonable_encoder(errors),
            },
        },
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Catches unexpected database exceptions at the application boundary.
    Logs diagnostic details internally while strictly preventing connection strings,
    database schemas, or SQL queries from leaking to external clients.
    """
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Database error [request_id={request_id}]: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.DATABASE_ERROR,
                "message": "A database error occurred. Please try again later.",
                "details": {},
            },
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled server exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(f"Unhandled server error [request_id={request_id}]: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred. Please try again later.",
                "details": {},
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers all domain and system exception handlers onto the application."""
    app.add_exception_handler(BloopException, bloop_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

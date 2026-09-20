"""
Bloop Authentication & Authorization Domain Exceptions
Defines typed exceptions with standard machine-readable error codes and HTTP statuses.
"""

from fastapi import status
from backend.app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    ValidationException,
    ErrorCode,
)


class InvalidCredentialsException(AuthenticationException):
    """Raised when authentication credentials (email/password) fail verification."""

    def __init__(self, message: str = "Invalid email or password."):
        super().__init__(
            message=message,
            code="INVALID_CREDENTIALS",
        )


class TokenExpiredException(AuthenticationException):
    """Raised when a JWT access token has expired."""

    def __init__(self, message: str = "Authentication token has expired."):
        super().__init__(
            message=message,
            code="TOKEN_EXPIRED",
        )


class TokenInvalidException(AuthenticationException):
    """Raised when a JWT token signature, payload, or structure is invalid."""

    def __init__(self, message: str = "Invalid authentication token."):
        super().__init__(
            message=message,
            code="INVALID_TOKEN",
        )


class AccountInactiveException(AuthenticationException):
    """Raised when an authenticated user's account is deactivated or inactive."""

    def __init__(self, message: str = "Account is inactive."):
        super().__init__(
            message=message,
            code="ACCOUNT_INACTIVE",
        )


class AccessDeniedException(AuthorizationException):
    """Raised when a user is authenticated but not authorized to access a resource."""

    def __init__(self, message: str = "Access denied. Insufficient permissions."):
        super().__init__(
            message=message,
            code="ACCESS_DENIED",
        )


class DuplicateEmailException(ConflictException):
    """Raised when registration is attempted with an existing email address."""

    def __init__(self, email: str):
        super().__init__(
            message="An account with this email address already exists.",
            details={"email": email},
            code="CONFLICT",
        )


class PasswordValidationException(ValidationException):
    """Raised when a submitted password violates length or complexity policy."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": "password"},
        )

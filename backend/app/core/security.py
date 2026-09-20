"""
Bloop Core Security Facade
Provides core security helpers and cryptographic primitives.
Maintains backward compatibility by delegating to backend.app.services.auth.
"""

from datetime import timedelta
from typing import Any, Optional, Union

from backend.app.core.config import settings
from backend.app.services.auth.jwt import (
    create_access_token as auth_create_access_token,
    decode_access_token as auth_decode_access_token,
)
from backend.app.services.auth.password import (
    hash_password as auth_hash_password,
    verify_password as auth_verify_password,
)

ALGORITHM = settings.JWT_ALGORITHM


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the hashed password using bcrypt."""
    return auth_verify_password(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a password with bcrypt salt and policy validation."""
    return auth_hash_password(password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Encodes a cryptographically signed JWT access token."""
    return auth_create_access_token(subject=subject, expires_delta=expires_delta)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT token signature and claims."""
    return auth_decode_access_token(token)

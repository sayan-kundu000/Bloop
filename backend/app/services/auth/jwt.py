"""
Bloop JWT Security Module
Handles cryptographically signed JSON Web Token (JWT) issuance, decoding,
algorithm enforcement, and claim validation according to Bloop security architecture.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import jwt

from backend.app.core.config import settings
from backend.app.services.auth.exceptions import (
    TokenExpiredException,
    TokenInvalidException,
)


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Issues a cryptographically signed JWT access token.
    Claims:
    - sub: stable user identifier string (canonical reference to User.id)
    - iat: issued-at timestamp (UTC)
    - exp: expiration timestamp (UTC)
    Uses the configured secret key and explicitly restricted algorithm (HS256).
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodes and cryptographically verifies an incoming JWT access token.
    Enforces expiration (exp) and strictly restricts algorithms to the configured algorithm.
    Returns the decoded claims dictionary on success, or None on failure.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "iat", "sub"]},
        )
        return payload
    except (jwt.PyJWTError, Exception):
        return None


def validate_token_claims(payload: Optional[dict]) -> int:
    """
    Validates decoded token payload claims and extracts the canonical integer User ID.
    Raises TokenInvalidException or TokenExpiredException if claims are invalid or missing.
    """
    if not payload:
        raise TokenInvalidException("Authentication token is invalid or corrupted.")

    sub = payload.get("sub")
    if sub is None:
        raise TokenInvalidException("Token subject claim is missing.")

    try:
        user_id = int(sub)
        return user_id
    except (ValueError, TypeError):
        raise TokenInvalidException("Token subject claim contains an invalid user identifier.")

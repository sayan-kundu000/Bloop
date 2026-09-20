"""
Bloop API Dependencies
Provides reusable FastAPI parameter dependencies for authentication,
authorization, database sessions, configuration, and service layers.
Supports dual credential transport: secure HttpOnly session cookies and Bearer tokens.
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import httpx
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, settings
from backend.app.core.http_client import get_http_client as get_managed_http_client
from backend.app.core.security import decode_access_token
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.services.auth.session import extract_token_from_request
from backend.app.services.auth_service import AuthService
from backend.app.services.quantum_service import QuantumService
from backend.app.services.tts_service import TTSService
from backend.app.services.voice_service import VoiceService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False)


def get_settings(request: Request) -> Settings:
    """Provides application configuration settings, respecting app-scoped instances."""
    if hasattr(request.app.state, "settings") and request.app.state.settings is not None:
        return request.app.state.settings
    return settings


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    bearer_token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """
    Validates JWT session credentials and resolves the authenticated User entity.
    Supports credentials from:
    1. HttpOnly browser session cookie ('access_token' or 'bloop_session')
    2. Authorization: Bearer <token> HTTP header
    Raises HTTP 401 if missing, invalid, expired, or user account is inactive.
    """
    token = bearer_token or extract_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTHENTICATION_REQUIRED", "message": "Authentication required. Session token missing."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid or expired authentication credentials."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Token payload contains invalid user ID."},
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "ACCOUNT_INACTIVE", "message": "User account is inactive or not found."},
        )
    return user


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
    bearer_token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Resolves authenticated User if a valid session cookie or Bearer token is provided;
    otherwise returns None without raising an authentication exception.
    """
    token = bearer_token or extract_token_from_request(request)
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        if not payload or "sub" not in payload:
            return None
        user_id = int(payload["sub"])
        user = UserRepository(db).get_by_id(user_id)
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Verifies that the authenticated user possesses superuser privileges."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCESS_DENIED", "message": "The user does not have superuser privileges."},
        )
    return current_user


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Resolves the managed reusable HTTP client from application state."""
    if hasattr(request.app.state, "http_client") and request.app.state.http_client is not None:
        return request.app.state.http_client
    return get_managed_http_client()


# ============================================================================
# Service Factory Dependencies
# ============================================================================

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Provides an instance of AuthService scoped to the current database session."""
    return AuthService(db)


def get_voice_service(db: Session = Depends(get_db)) -> VoiceService:
    """Provides an instance of VoiceService scoped to the current database session."""
    return VoiceService(db)


def get_speech_service(db: Session = Depends(get_db)) -> TTSService:
    """Provides an instance of TTSService scoped to the current database session."""
    return TTSService(db)


def get_quantum_service(db: Session = Depends(get_db)) -> QuantumService:
    """Provides an instance of QuantumService scoped to the current database session."""
    return QuantumService(db)

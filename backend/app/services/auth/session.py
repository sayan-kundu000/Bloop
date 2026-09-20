"""
Bloop Session Management & Secure Cookie Architecture
Handles secure HTTP-only cookie configuration for browser sessions and
safe token extraction supporting both cookies and Authorization headers.
"""

from typing import Optional
from fastapi import Request, Response

from backend.app.core.config import Settings, settings as global_settings

SESSION_COOKIE_NAME = "access_token"
LEGACY_SESSION_COOKIE_NAME = "bloop_session"


def get_cookie_security_params(cfg: Settings) -> dict:
    """
    Derives secure cookie attributes based on the active runtime environment profile.
    - Production: HttpOnly, Secure=True, SameSite='none' (for cross-origin Vercel + Render) or 'lax'.
    - Development/Test: HttpOnly, Secure=False, SameSite='lax' for local testing on http://localhost.
    """
    is_prod = (cfg.APP_ENV == "production")
    # For cross-origin Render (API) and Vercel (Frontend), SameSite=None is required alongside Secure=True
    samesite = "none" if is_prod else "lax"
    secure = is_prod

    return {
        "httponly": True,
        "secure": secure,
        "samesite": samesite,
        "path": "/",
        "max_age": cfg.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


def set_session_cookie(
    response: Response,
    token: str,
    cfg: Optional[Settings] = None,
) -> None:
    """
    Attaches the JWT access token to the outgoing HTTP response as an HttpOnly,
    Secure, SameSite-controlled session cookie.
    """
    active_cfg = cfg or global_settings
    params = get_cookie_security_params(active_cfg)

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=params["httponly"],
        secure=params["secure"],
        samesite=params["samesite"],
        path=params["path"],
        max_age=params["max_age"],
    )


def clear_session_cookie(
    response: Response,
    cfg: Optional[Settings] = None,
) -> None:
    """
    Terminates the user session by clearing the HttpOnly session cookie.
    Matches path and security parameters to ensure browser cache and storage purging.
    """
    active_cfg = cfg or global_settings
    params = get_cookie_security_params(active_cfg)

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path=params["path"],
        secure=params["secure"],
        httponly=params["httponly"],
        samesite=params["samesite"],
    )
    # Also clear legacy alias if present
    response.delete_cookie(
        key=LEGACY_SESSION_COOKIE_NAME,
        path=params["path"],
        secure=params["secure"],
        httponly=params["httponly"],
        samesite=params["samesite"],
    )


def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extracts authentication JWT credential from the incoming HTTP request:
    1. Checks HttpOnly session cookie ('access_token' or 'bloop_session').
    2. Falls back to standard 'Authorization: Bearer <token>' header.
    Returns the token string if present, or None if anonymous.
    """
    # 1. Primary: Session Cookie
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        token = request.cookies.get(LEGACY_SESSION_COOKIE_NAME)
    if token:
        return token

    # 2. Secondary / API Fallback: Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()

    return None

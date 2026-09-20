"""
Bloop Authentication Domain Package
Exposes core identity, password, JWT, session, and exception abstractions.
"""

from backend.app.services.auth.exceptions import (
    AccessDeniedException,
    AccountInactiveException,
    DuplicateEmailException,
    InvalidCredentialsException,
    PasswordValidationException,
    TokenExpiredException,
    TokenInvalidException,
)
from backend.app.services.auth.jwt import (
    create_access_token,
    decode_access_token,
    validate_token_claims,
)
from backend.app.services.auth.password import (
    hash_password,
    validate_password_policy,
    verify_password,
)
from backend.app.services.auth.service import AuthService
from backend.app.services.auth.session import (
    clear_session_cookie,
    extract_token_from_request,
    get_cookie_security_params,
    set_session_cookie,
)

__all__ = [
    "AuthService",
    "hash_password",
    "verify_password",
    "validate_password_policy",
    "create_access_token",
    "decode_access_token",
    "validate_token_claims",
    "set_session_cookie",
    "clear_session_cookie",
    "extract_token_from_request",
    "get_cookie_security_params",
    "InvalidCredentialsException",
    "TokenExpiredException",
    "TokenInvalidException",
    "AccountInactiveException",
    "AccessDeniedException",
    "DuplicateEmailException",
    "PasswordValidationException",
]

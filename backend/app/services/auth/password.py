"""
Bloop Password Security Module
Implements secure password hashing, timing-safe verification, and policy enforcement.
Strictly relies on established, salted adaptive cryptographic hashing (bcrypt).
"""

import bcrypt
from backend.app.services.auth.exceptions import PasswordValidationException

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 100


def validate_password_policy(password: str) -> None:
    """
    Enforces application password security policy prior to persistence.
    Rejects missing, empty, whitespace-only, and out-of-boundary passwords.
    Never returns or logs the raw password.
    """
    if not password or not password.strip():
        raise PasswordValidationException("Password is required and cannot be blank.")
    
    if len(password) < MIN_PASSWORD_LENGTH:
        raise PasswordValidationException(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
        )
    
    if len(password) > MAX_PASSWORD_LENGTH:
        raise PasswordValidationException(
            f"Password cannot exceed {MAX_PASSWORD_LENGTH} characters."
        )


def hash_password(password: str) -> str:
    """
    Hashes a plain password using bcrypt with an automatically generated salt.
    Enforces policy validation before hashing.
    """
    validate_password_policy(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the stored bcrypt hash.
    Employs bcrypt's constant-time comparison to protect against timing attacks.
    Returns False on any malformed hash or verification error without leaking exceptions.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False

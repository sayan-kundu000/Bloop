"""
Bloop Authentication Schemas
Request and response contracts for user registration, authentication, token issuance, and logout.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from backend.app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    """Request schema for new account registration."""
    email: EmailStr = Field(..., description="Valid user email address")
    password: str = Field(..., min_length=6, max_length=100, description="Plaintext password (min 6 chars)")
    full_name: Optional[str] = Field(None, max_length=100, description="Optional user full name")


class LoginRequest(BaseModel):
    """Request schema for user credential login."""
    email: EmailStr = Field(..., description="Registered user email address")
    password: str = Field(..., description="Account password")


class TokenResponse(BaseModel):
    """Response schema returned upon successful registration or login."""
    access_token: str = Field(..., description="Cryptographically signed JWT Bearer access token")
    token_type: str = Field("bearer", description="Token scheme identifier")
    user: UserResponse = Field(..., description="Authenticated user profile details")


# Backward compatibility aliases
UserCreate = RegisterRequest
UserLogin = LoginRequest
Token = TokenResponse


class LogoutResponse(BaseModel):
    """Response schema confirming successful session termination."""
    logged_out: bool = Field(True, description="Indicates successful client-side logout")
    message: str = Field("Logged out successfully.", description="Informational message")

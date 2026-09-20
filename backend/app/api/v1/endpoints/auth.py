"""
Bloop Authentication Endpoints
Handles user registration, login, JWT token issuance, session cookies, and logout.
Enforces intermediate-level security architecture, rate limiting, and password policies.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_optional_current_user
from backend.app.core.config import settings
from backend.app.core.exceptions import (
    AuthenticationException,
    ConflictException,
    ErrorCode,
    ValidationException,
)
from backend.app.core.rate_limit import rate_limit
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import (
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    TokenResponse,
)
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.user import UserResponse
from backend.app.services.auth import (
    AccountInactiveException,
    AuthService,
    DuplicateEmailException,
    InvalidCredentialsException,
    PasswordValidationException,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_AUTH))],
)
def register(
    user_in: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Registers a new user account:
    - Validates email and password policy.
    - Hashes password with secure salt (bcrypt).
    - Checks for existing account (returns HTTP 409 on duplicate).
    - Issues JWT token and sets secure HttpOnly session cookie.
    """
    auth_service = AuthService(db)
    try:
        token_data = auth_service.register_user(user_in, response=response)
        return ApiResponse(
            success=True,
            data=token_data,
            message="Registration successful.",
        )
    except DuplicateEmailException:
        raise
    except PasswordValidationException:
        raise
    except ValueError as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            raise ConflictException(error_msg, details={"email": user_in.email})
        raise ValidationException(error_msg, details={"error": error_msg})


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    dependencies=[Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_AUTH))],
)
def login(
    login_in: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Authenticates user credentials:
    - Normalizes email and verifies bcrypt password hash.
    - Returns generic INVALID_CREDENTIALS error on non-existent account or wrong password.
    - Rejects inactive accounts with ACCOUNT_INACTIVE error.
    - Issues signed JWT token and sets secure HttpOnly session cookie.
    """
    auth_service = AuthService(db)
    try:
        token_data = auth_service.authenticate_user(login_in, response=response)
        return ApiResponse(
            success=True,
            data=token_data,
            message="Login successful.",
        )
    except (InvalidCredentialsException, AccountInactiveException):
        raise
    except ValueError as e:
        raise AuthenticationException(str(e), code=ErrorCode.INVALID_CREDENTIALS)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": ErrorCode.ACCESS_DENIED, "message": str(e)},
        )


@router.post("/logout", response_model=ApiResponse[LogoutResponse])
def logout(
    response: Response,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Terminates the active session and clears the secure HttpOnly session cookie.
    """
    auth_service = AuthService(db)
    logout_res = auth_service.logout_user(response)
    return ApiResponse(
        success=True,
        data=logout_res,
        message="Logged out successfully.",
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Retrieves the authenticated user's safe profile details.
    Requires active session cookie or Bearer authorization header.
    """
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(current_user),
        message="Current user profile retrieved.",
    )

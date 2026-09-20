"""
Bloop Centralized Authentication Service
Coordinates user registration, credential authentication, session management,
and user entity resolution. Strictly enforces security boundaries and password policies.
"""

from typing import Optional
from fastapi import Response
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.user_preference import UserPreference
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import (
    LoginRequest,
    LogoutResponse,
    RegisterRequest,
    TokenResponse,
)
from backend.app.schemas.user import UserResponse
from backend.app.services.auth.exceptions import (
    AccountInactiveException,
    DuplicateEmailException,
    InvalidCredentialsException,
)
from backend.app.services.auth.jwt import create_access_token
from backend.app.services.auth.password import (
    hash_password,
    validate_password_policy,
    verify_password,
)
from backend.app.services.auth.session import clear_session_cookie, set_session_cookie


class AuthService:
    """
    Centralized Identity & Authentication Service.
    Answers: 'Who is this user?' and issues authenticated JWT sessions.
    """

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(
        self,
        user_in: RegisterRequest,
        response: Optional[Response] = None,
    ) -> TokenResponse:
        """
        Registers a new user account:
        1. Normalizes email (trim and lowercase).
        2. Validates password against length/complexity policies.
        3. Verifies email uniqueness, preventing race-conditions via DB constraints.
        4. Hashes password with adaptive salted bcrypt.
        5. Persists User record and creates default preferences.
        6. Issues JWT access token and attaches secure HttpOnly session cookie.
        """
        clean_email = user_in.email.lower().strip()

        # Enforce password policy
        validate_password_policy(user_in.password)

        # Check existing account
        existing_user = self.user_repo.get_by_email(clean_email)
        if existing_user:
            raise DuplicateEmailException(clean_email)

        # Create user record
        hashed_pwd = hash_password(user_in.password)
        user = User(
            email=clean_email,
            hashed_password=hashed_pwd,
            full_name=user_in.full_name,
            is_active=True,
            is_superuser=False,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Initialize default user preferences
        pref = UserPreference(user_id=user.id)
        self.db.add(pref)
        self.db.commit()

        # Issue JWT access token
        token_str = create_access_token(subject=user.id)

        # Set secure HttpOnly session cookie if response is available
        if response is not None:
            set_session_cookie(response, token_str)

        return TokenResponse(
            access_token=token_str,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    def authenticate_user(
        self,
        login_in: LoginRequest,
        response: Optional[Response] = None,
    ) -> TokenResponse:
        """
        Authenticates user credentials:
        1. Normalizes email.
        2. Looks up user in database.
        3. Verifies password using timing-safe bcrypt hash check.
        4. Enforces active account status.
        5. Issues JWT access token and attaches secure HttpOnly session cookie.
        """
        clean_email = login_in.email.lower().strip()
        user = self.user_repo.get_by_email(clean_email)

        # Timing-safe password verification; evaluate even if user is None to mitigate timing enumeration
        dummy_hash = "$2b$12$e8Y69h1Z6vL2mY4C9uJ2Ae6Z9sB5mX8qR1wV3yT7kP0nO4lM5kP0e"
        valid_password = verify_password(
            login_in.password,
            user.hashed_password if user else dummy_hash,
        )

        if not user or not valid_password:
            raise InvalidCredentialsException()

        if not user.is_active:
            raise AccountInactiveException()

        token_str = create_access_token(subject=user.id)

        if response is not None:
            set_session_cookie(response, token_str)

        return TokenResponse(
            access_token=token_str,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    def logout_user(self, response: Response) -> LogoutResponse:
        """
        Terminates the active session by purging the HttpOnly session cookie.
        """
        clear_session_cookie(response)
        return LogoutResponse(
            logged_out=True,
            message="User session terminated successfully.",
        )

    def resolve_current_user(self, user_id: int) -> Optional[User]:
        """
        Resolves a User entity by canonical ID.
        """
        return self.user_repo.get_by_id(user_id)

    # ------------------------------------------------------------------------
    # Backward-Compatibility Methods for Existing Prompts
    # ------------------------------------------------------------------------
    def register(self, user_in: RegisterRequest, response: Optional[Response] = None) -> TokenResponse:
        return self.register_user(user_in, response=response)

    def login(self, login_in: LoginRequest, response: Optional[Response] = None) -> TokenResponse:
        return self.authenticate_user(login_in, response=response)

    def get_current_user(self, user_id: int) -> Optional[User]:
        return self.resolve_current_user(user_id)

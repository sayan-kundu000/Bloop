"""
Bloop User Domain Service
Encapsulates business logic for user profile retrieval, safe profile mutations, and user lookups.
"""

from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.user_preference import UserPreference
from backend.app.repositories.user import UserRepository
from backend.app.repositories.user_preference import UserPreferenceRepository
from backend.app.schemas.user import UserDetailResponse, UserProfileUpdateRequest, UserUpdate
from backend.app.core.exceptions import ResourceNotFoundException, ValidationException


class UserService:
    """Service handling profile retrieval, safe profile modification, and user entity lookups."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.pref_repo = UserPreferenceRepository(db)

    def get_profile(self, user: User) -> UserDetailResponse:
        """
        Retrieve the full user profile including preferences.
        Guarantees that a default preference record exists if not already present.
        """
        if not user.preference:
            pref = self.pref_repo.get_or_create(user.id)
            user.preference = pref

        return UserDetailResponse.model_validate(user)

    def update_profile(
        self,
        user: User,
        profile_in: UserProfileUpdateRequest | UserUpdate,
    ) -> UserDetailResponse:
        """
        Update permitted user profile details (full_name) transactionally.
        Strictly enforces that passwords, email, and security fields cannot be modified
        through the profile endpoint (Prompt 15 §8).
        """
        full_name: Optional[str] = None
        if profile_in.full_name is not None:
            clean_name = profile_in.full_name.strip()
            if len(clean_name) > 100:
                raise ValidationException("Display name cannot exceed 100 characters.")
            full_name = clean_name if clean_name else None

        updated_user = self.user_repo.update_profile(user, full_name)

        if not updated_user.preference:
            pref = self.pref_repo.get_or_create(updated_user.id)
            updated_user.preference = pref

        return UserDetailResponse.model_validate(updated_user)

    def get_user_by_id(self, user_id: int) -> UserDetailResponse:
        """
        Retrieve a user profile by ID (typically for superusers/administrative use).
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundException(resource="User", identifier=user_id)

        if not user.preference:
            pref = self.pref_repo.get_or_create(user.id)
            user.preference = pref

        return UserDetailResponse.model_validate(user)

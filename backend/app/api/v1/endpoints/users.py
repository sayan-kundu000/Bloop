"""
Bloop Users API Endpoints
Provides profile management, personalization preferences, and identity operations.
Built with thin route handlers delegating to UserService and PreferenceService (Prompt 15 §33).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_active_superuser, get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.common import ApiResponse
from backend.app.schemas.user import (
    UserDetailResponse,
    UserPreferenceResponse,
    UserPreferenceUpdate,
    UserProfileUpdateRequest,
    UserUpdate,
)
from backend.app.services.users.service import UserService
from backend.app.services.preferences.service import PreferenceService

router = APIRouter()


@router.get("/me", response_model=ApiResponse[UserDetailResponse])
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the complete profile and preferences for the currently authenticated user.
    """
    user_service = UserService(db)
    profile = user_service.get_profile(current_user)

    return ApiResponse(
        success=True,
        data=profile,
        message="User profile retrieved successfully."
    )


@router.patch("/me", response_model=ApiResponse[UserDetailResponse])
def update_current_user_profile(
    user_in: UserProfileUpdateRequest | UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates the authenticated user's permitted profile details (display name).
    Excludes passwords and security fields (Prompt 15 §8).
    """
    user_service = UserService(db)
    updated_profile = user_service.update_profile(current_user, user_in)

    return ApiResponse(
        success=True,
        data=updated_profile,
        message="User profile updated successfully."
    )


@router.get("/me/preferences", response_model=ApiResponse[UserPreferenceResponse])
def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves user UI and speech generation preferences (Prompt 15 §11).
    """
    pref_service = PreferenceService(db)
    prefs = pref_service.get_preferences(current_user.id)

    return ApiResponse(
        success=True,
        data=prefs,
        message="Preferences retrieved successfully."
    )


@router.patch("/me/preferences", response_model=ApiResponse[UserPreferenceResponse])
def update_user_preferences(
    prefs_in: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates UI settings, audio playback speed, and theme preferences for the authenticated user.
    """
    pref_service = PreferenceService(db)
    updated_prefs = pref_service.update_preferences(current_user.id, prefs_in)

    return ApiResponse(
        success=True,
        data=updated_prefs,
        message="Preferences updated successfully."
    )


@router.get("/{user_id}", response_model=ApiResponse[UserDetailResponse])
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_superuser),
):
    """
    Administrative endpoint to retrieve user profile by ID. Requires superuser privileges.
    """
    user_service = UserService(db)
    user_profile = user_service.get_user_by_id(user_id)

    return ApiResponse(
        success=True,
        data=user_profile,
        message="User retrieved successfully."
    )

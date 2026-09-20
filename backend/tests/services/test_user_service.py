"""
Bloop User Service Automated Tests
Validates profile retrieval, safe profile mutations, and immutable field protections (Prompt 15 §8).
"""

import pytest
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.user_preference import UserPreference
from backend.app.services.users.service import UserService
from backend.app.schemas.user import UserProfileUpdateRequest, UserUpdate
from backend.app.core.exceptions import ResourceNotFoundException, ValidationException


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Fixture creating a test user without initial preferences."""
    import uuid
    user = User(
        email=f"profile_test_{uuid.uuid4().hex[:8]}@bloop.ai",
        hashed_password="hashed_secret_password",
        full_name="Original Name",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestUserService:
    """Tests for UserService profile operations and security invariants."""

    def test_get_profile_returns_user_and_initializes_preferences(
        self, db_session: Session, test_user: User
    ):
        service = UserService(db_session)
        profile = service.get_profile(test_user)

        assert profile.id == test_user.id
        assert profile.email == test_user.email
        assert profile.full_name == "Original Name"
        assert profile.preference is not None
        assert profile.preference.theme == "dark"
        assert profile.preference.audio_speed == 1.0

    def test_update_profile_updates_full_name(
        self, db_session: Session, test_user: User
    ):
        service = UserService(db_session)
        req = UserProfileUpdateRequest(full_name="Updated Display Name")
        profile = service.update_profile(test_user, req)

        assert profile.full_name == "Updated Display Name"

        # Verify database persistence
        db_user = db_session.query(User).filter(User.id == test_user.id).first()
        assert db_user.full_name == "Updated Display Name"

    def test_update_profile_strips_whitespace_and_handles_empty(
        self, db_session: Session, test_user: User
    ):
        service = UserService(db_session)
        req = UserProfileUpdateRequest(full_name="   Padded Name   ")
        profile = service.update_profile(test_user, req)
        assert profile.full_name == "Padded Name"

        # Empty string turns to None
        req_empty = UserProfileUpdateRequest(full_name="   ")
        profile_empty = service.update_profile(test_user, req_empty)
        assert profile_empty.full_name is None

    def test_update_profile_rejects_oversized_name(
        self, db_session: Session, test_user: User
    ):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UserProfileUpdateRequest(full_name="A" * 105)


    def test_update_profile_does_not_modify_password_or_immutable_fields(
        self, db_session: Session, test_user: User
    ):
        original_hash = test_user.hashed_password
        original_email = test_user.email
        original_id = test_user.id
        original_superuser = test_user.is_superuser

        service = UserService(db_session)
        # Even if legacy UserUpdate with password or extra fields is passed
        req = UserUpdate(full_name="Safe Name", password="malicious_new_password")
        service.update_profile(test_user, req)

        db_session.refresh(test_user)
        assert test_user.id == original_id
        assert test_user.email == original_email
        assert test_user.is_superuser == original_superuser
        # Password remains unchanged because profile update only touches permitted fields
        assert test_user.hashed_password == original_hash

    def test_get_user_by_id_superuser_lookup(
        self, db_session: Session, test_user: User
    ):
        service = UserService(db_session)
        user_detail = service.get_user_by_id(test_user.id)
        assert user_detail.id == test_user.id

        with pytest.raises(ResourceNotFoundException):
            service.get_user_by_id(99999999)

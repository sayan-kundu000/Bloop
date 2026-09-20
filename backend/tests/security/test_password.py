"""
Bloop Password Security Unit Tests
Verifies password hashing, salting uniqueness, timing-safe verification,
and password policy boundaries.
"""

import pytest
from backend.app.services.auth.exceptions import PasswordValidationException
from backend.app.services.auth.password import (
    hash_password,
    validate_password_policy,
    verify_password,
)


class TestPasswordSecurity:
    """Verifies security, salting, verification, and validation of passwords."""

    def test_password_hashing_and_verification(self):
        plain = "CorrectHorseBatteryStaple123"
        hashed = hash_password(plain)

        # Hash must not contain plaintext
        assert plain not in hashed
        assert hashed.startswith("$2b$")

        # Verification succeeds with correct password
        assert verify_password(plain, hashed) is True

        # Verification fails with wrong password
        assert verify_password("WrongPassword123", hashed) is False

    def test_salting_uniqueness(self):
        """Identical passwords must generate different hashes due to random salting."""
        password = "SecurePassword@12345"
        hash_1 = hash_password(password)
        hash_2 = hash_password(password)

        assert hash_1 != hash_2
        assert verify_password(password, hash_1) is True
        assert verify_password(password, hash_2) is True

    def test_empty_and_whitespace_password_rejected(self):
        with pytest.raises(PasswordValidationException) as exc_info:
            hash_password("")
        assert "blank" in str(exc_info.value).lower()

        with pytest.raises(PasswordValidationException) as exc_info:
            hash_password("     ")
        assert "blank" in str(exc_info.value).lower()

    def test_minimum_password_length_enforced(self):
        with pytest.raises(PasswordValidationException) as exc_info:
            hash_password("12345")
        assert "at least 6" in str(exc_info.value).lower()

    def test_maximum_password_length_enforced(self):
        oversized = "a" * 101
        with pytest.raises(PasswordValidationException) as exc_info:
            hash_password(oversized)
        assert "cannot exceed 100" in str(exc_info.value).lower()

    def test_verify_password_safe_with_invalid_hashes(self):
        """Must return False without throwing unhandled exceptions on corrupt hashes."""
        assert verify_password("some_password", "") is False
        assert verify_password("", "some_hash") is False
        assert verify_password("some_password", "not-a-valid-bcrypt-hash") is False
        assert verify_password("some_password", "$2b$12$invalid_hash_truncated") is False

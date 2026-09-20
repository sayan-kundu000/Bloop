"""
Bloop JWT Security Unit Tests
Verifies token issuance, cryptographic verification, expiration enforcement,
claims validation, and algorithm restrictions.
"""

from datetime import timedelta
import jwt
import pytest

from backend.app.core.config import settings
from backend.app.services.auth.exceptions import TokenInvalidException
from backend.app.services.auth.jwt import (
    create_access_token,
    decode_access_token,
    validate_token_claims,
)


class TestJWTSecurity:
    """Verifies JWT security invariants and claims validation."""

    def test_create_and_decode_valid_token(self):
        user_id = 42
        token = create_access_token(subject=user_id)
        assert isinstance(token, str)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert "exp" in payload
        assert "iat" in payload

        resolved_id = validate_token_claims(payload)
        assert resolved_id == user_id

    def test_expired_token_rejected(self):
        # Create token that expired 10 minutes ago
        past_delta = timedelta(minutes=-10)
        expired_token = create_access_token(subject=100, expires_delta=past_delta)

        payload = decode_access_token(expired_token)
        assert payload is None

    def test_invalid_signature_rejected(self):
        valid_token = create_access_token(subject=1)
        # Attempt to decode with a different secret
        other_secret = "different-secret-key-that-does-not-match-settings-32chars"
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(valid_token, other_secret, algorithms=[settings.JWT_ALGORITHM])

        # decode_access_token returns None on tampered tokens
        tampered_token = valid_token[:-6] + "abcdef"
        assert decode_access_token(tampered_token) is None

    def test_malformed_token_rejected(self):
        assert decode_access_token("not.a.valid.jwt") is None
        assert decode_access_token("") is None
        assert decode_access_token("header.payload") is None

    def test_validate_token_claims_missing_or_invalid_sub(self):
        with pytest.raises(TokenInvalidException) as exc_1:
            validate_token_claims(None)
        assert "invalid" in str(exc_1.value).lower()

        with pytest.raises(TokenInvalidException) as exc_2:
            validate_token_claims({"exp": 1234567890})
        assert "missing" in str(exc_2.value).lower()

        with pytest.raises(TokenInvalidException) as exc_3:
            validate_token_claims({"sub": "not-an-integer-id"})
        assert "invalid" in str(exc_3.value).lower()

    def test_untrusted_algorithm_rejected(self):
        """Tokens signed with unsupported or 'none' algorithm must fail verification."""
        unsigned_token = jwt.encode({"sub": "1"}, key="", algorithm="none")
        payload = decode_access_token(unsigned_token)
        assert payload is None

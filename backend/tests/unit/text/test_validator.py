"""
Unit Tests — Text Validator
Validates Level 2 text validation rules: empty text rejection, whitespace-only
rejection, boundary constraints, and maximum character length enforcement.
"""

import pytest
from backend.app.core.exceptions import ErrorCode, TextEmptyException, TextTooLongException
from backend.app.services.text.validator import TextValidator


class TestTextValidator:
    """Tests Level 2 TextValidator rules and exceptions."""

    @pytest.fixture
    def validator(self):
        return TextValidator(min_characters=1, max_characters=2500)

    def test_empty_string_raises_text_empty(self, validator):
        with pytest.raises(TextEmptyException) as exc_info:
            validator.validate("")
        exc = exc_info.value
        assert exc.code == ErrorCode.TEXT_EMPTY
        assert exc.status_code == 422
        assert "empty" in exc.message.lower()

    def test_whitespace_only_string_raises_text_empty(self, validator):
        with pytest.raises(TextEmptyException) as exc_info:
            validator.validate("   \n\t  \r\n  ")
        exc = exc_info.value
        assert exc.code == ErrorCode.TEXT_EMPTY
        assert exc.status_code == 422

    def test_none_input_raises_text_empty(self, validator):
        with pytest.raises(TextEmptyException) as exc_info:
            validator.validate(None)
        assert exc_info.value.code == ErrorCode.TEXT_EMPTY

    def test_valid_text_within_limits_returns_metrics(self, validator):
        sample = "Valid speech synthesis text."
        metrics = validator.validate(sample)
        assert metrics.normalized_text == sample
        assert metrics.character_count == len(sample)
        assert metrics.word_count == 4
        assert metrics.is_empty is False

    def test_exact_boundary_text_succeeds(self, validator):
        exact_text = "A" * 2500
        metrics = validator.validate(exact_text)
        assert metrics.character_count == 2500

    def test_oversized_text_raises_text_too_long(self, validator):
        oversized = "A" * 2501
        with pytest.raises(TextTooLongException) as exc_info:
            validator.validate(oversized)
        exc = exc_info.value
        assert exc.code == ErrorCode.TEXT_TOO_LONG
        assert exc.status_code == 422
        assert exc.details["max_characters"] == 2500
        assert exc.details["actual_characters"] == 2501

    def test_custom_max_characters_override(self, validator):
        text = "Hello world from Bloop"  # 22 chars
        # With override of 20, should fail
        with pytest.raises(TextTooLongException) as exc_info:
            validator.validate(text, max_chars_override=20)
        assert exc_info.value.code == ErrorCode.TEXT_TOO_LONG
        assert exc_info.value.details["max_characters"] == 20

        # With override of 30, should pass
        metrics = validator.validate(text, max_chars_override=30)
        assert metrics.character_count == 22

    def test_database_independence(self):
        # Verify validator executes with zero DB session or ORM dependency
        val = TextValidator(min_characters=1, max_characters=100)
        res = val.validate("Offline standalone validation test")
        assert res.character_count == 34

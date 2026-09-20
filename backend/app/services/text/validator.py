"""
Bloop Text Validator Module
Enforces Level 2 text validation rules: presence, whitespace-only rejection,
character boundary constraints, and metrics validation.
"""

from typing import Optional
from backend.app.core.config import settings
from backend.app.core.exceptions import TextEmptyException, TextTooLongException
from backend.app.services.text.metrics import TextMetrics
from backend.app.services.text.processor import calculate_metrics, normalize_text


class TextValidator:
    """
    Authoritative Level 2 Text Validation Engine.
    Validates submitted strings against application limits and ensures text is
    present, meaningful, and safe for speech synthesis.
    """

    def __init__(
        self,
        min_characters: Optional[int] = None,
        max_characters: Optional[int] = None,
        speaking_rate_wpm: float = 150.0,
    ):
        self.min_characters = min_characters if min_characters is not None else getattr(settings, "MIN_TEXT_CHARACTERS", 1)
        self.max_characters = max_characters if max_characters is not None else getattr(settings, "MAX_TEXT_CHARACTERS", 2500)
        self.speaking_rate_wpm = speaking_rate_wpm

    def validate(
        self,
        text: Optional[str],
        max_chars_override: Optional[int] = None,
    ) -> TextMetrics:
        """
        Validates input text and returns calculated TextMetrics upon success.

        Validation Steps:
        1. Presence / Empty Check:
           If text is None, empty string, or solely whitespace after normalization,
           raises TextEmptyException (HTTP 422, code: TEXT_EMPTY).
        2. Length Constraint Check:
           If normalized character count exceeds max_characters,
           raises TextTooLongException (HTTP 422, code: TEXT_TOO_LONG).
        3. Returns authoritative TextMetrics containing normalized text and metrics.

        Raises:
            TextEmptyException: If text is empty or whitespace-only.
            TextTooLongException: If text character count exceeds the configured limit.
        """
        max_limit = max_chars_override if max_chars_override is not None else self.max_characters

        # 1. Normalize
        normalized = normalize_text(text)

        # 2. Level 2 Presence Check
        if not normalized:
            raise TextEmptyException(
                message="Text cannot be empty",
                details={"reason": "empty_or_whitespace_only"},
            )

        # 3. Derive metrics
        metrics = calculate_metrics(normalized, speaking_rate_wpm=self.speaking_rate_wpm)

        # 4. Level 2 Maximum Limit Check
        if metrics.character_count > max_limit:
            raise TextTooLongException(
                message="Text exceeds the maximum allowed length",
                max_characters=max_limit,
                actual_characters=metrics.character_count,
            )

        return metrics

"""
Quantum Emotion Intelligence — Conservative Text Preprocessor
Normalizes Unicode, enforces character limits, and produces deterministic tokens
without semantic alteration, translation, or LLM hallucination.
"""

import re
import unicodedata
from typing import List
from backend.app.quantum.emotion.exceptions import EmotionResourceLimitException
from backend.app.core.exceptions import ValidationException


class EmotionTextPreprocessor:
    """
    Sanitizes raw text into normalized strings and tokens.
    Guarantees that input is strictly validated without changing user intent.
    """

    MAX_TEXT_LENGTH = 1000

    def preprocess(self, text: str) -> str:
        """
        Performs Unicode NFKC normalization, strips non-printable control characters,
        unifies CRLF newlines, and validates length bounds.
        """
        if text is None:
            raise ValidationException("Text input cannot be null.")

        # 1. Unicode NFKC normalization
        normalized = unicodedata.normalize("NFKC", text)

        # 2. Unify CRLF to standard LF and trim whitespace
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
        cleaned = normalized.strip()

        # 3. Empty & whitespace-only validation
        if not cleaned:
            raise ValidationException("Text cannot be empty or contain only whitespace.")

        # 4. Strip non-printable ASCII control characters (keep newline and tab)
        cleaned = "".join(ch for ch in cleaned if unicodedata.category(ch)[0] != "C" or ch in ("\n", "\t"))

        # 5. Length boundary enforcement
        if len(cleaned) > self.MAX_TEXT_LENGTH:
            raise EmotionResourceLimitException(
                f"Input text length ({len(cleaned)}) exceeds maximum allowable limit of {self.MAX_TEXT_LENGTH} characters."
            )

        return cleaned

    def tokenize(self, text: str) -> List[str]:
        """
        Extracts lowercase alphanumeric tokens using deterministic word boundaries.
        """
        cleaned = self.preprocess(text)
        tokens = re.findall(r"\b\w+\b", cleaned.lower(), flags=re.UNICODE)
        return tokens

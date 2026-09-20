"""
Bloop Quantum Text Preprocessing & Validation
Provides conservative, deterministic text cleaning and tokenization.
Guarantees semantic fidelity without paraphrasing, LLM rewrites, or translations.
"""

import re
import unicodedata
from typing import List, Optional
from backend.app.services.text.processor import normalize_text
from backend.app.quantum.text.exceptions import QuantumTextInvalidException

# Regex pattern for deterministic alphanumeric word tokenization
_TOKEN_PATTERN = re.compile(r"\b\w+\b", re.UNICODE)


class QuantumTextPreprocessor:
    """
    Validates and conservatively preprocesses text prompts for quantum NLP experiments.
    """

    def __init__(self, max_characters: int = 1000, min_characters: int = 1):
        self.max_characters = max_characters
        self.min_characters = min_characters

    def validate_and_clean(self, text: Optional[str]) -> str:
        """
        Validates text presence and boundary constraints, then applies conservative normalization.

        Raises:
            QuantumTextInvalidException: if text is None, empty, whitespace-only,
            or exceeds allowable character limits.
        """
        if text is None:
            raise QuantumTextInvalidException(
                message="Text prompt cannot be null.",
                details={"reason": "null_input"},
            )

        # 1. Base normalization (unifies line endings, strips control chars, strips edge whitespace)
        cleaned = normalize_text(text)

        if not cleaned:
            raise QuantumTextInvalidException(
                message="Text prompt cannot be empty or solely whitespace.",
                details={"reason": "empty_or_whitespace_only"},
            )

        # 2. Unicode normalization (NFKC ensures canonical composition and compatibility decomposition)
        cleaned = unicodedata.normalize("NFKC", cleaned)

        # 3. Boundary validation
        char_count = len(cleaned)
        if char_count < self.min_characters:
            raise QuantumTextInvalidException(
                message=f"Text length ({char_count}) is below minimum allowable length ({self.min_characters}).",
                details={"min_characters": self.min_characters, "actual_characters": char_count},
            )

        if char_count > self.max_characters:
            raise QuantumTextInvalidException(
                message=f"Text length ({char_count}) exceeds maximum allowable quantum experiment limit ({self.max_characters}).",
                details={"max_characters": self.max_characters, "actual_characters": char_count},
            )

        return cleaned

    def tokenize(self, text: str) -> List[str]:
        """Extracts deterministic word tokens in lowercase."""
        if not text:
            return []
        cleaned = unicodedata.normalize("NFKC", text.lower())
        return _TOKEN_PATTERN.findall(cleaned)

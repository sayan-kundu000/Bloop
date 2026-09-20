"""
Bloop Quantum Semantic Intelligence Preprocessing
Provides conservative text normalization, Unicode NFKC cleaning,
and strict input validation for the semantic similarity pipeline.
"""

import unicodedata
import re
from typing import Tuple
from backend.app.core.config import settings
from backend.app.quantum.semantic.exceptions import SemanticInputInvalidException


class SemanticPreprocessor:
    """Conservative preprocessor for semantic text analysis."""

    def __init__(self, max_length: int = 1000):
        configured_max = getattr(settings, "MAX_TEXT_CHARACTERS", 1000)
        self.max_length = min(max_length, configured_max)

    def clean_text(self, text: str) -> str:
        """
        Normalizes text conservatively:
        - Unicode NFKC normalization
        - Strips control characters
        - Normalizes whitespace
        """
        if not text:
            return ""

        # Normalize Unicode
        normalized = unicodedata.normalize("NFKC", text)

        # Remove control characters except standard whitespace
        cleaned = "".join(ch for ch in normalized if unicodedata.category(ch)[0] != "C" or ch in "\n\r\t")

        # Collapse whitespace
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def validate_pair(self, text_a: str, text_b: str) -> Tuple[str, str]:
        """
        Validates text pair for semantic similarity comparison.
        Raises SemanticInputInvalidException on invalid, empty, or oversized input.
        """
        cleaned_a = self.clean_text(text_a)
        cleaned_b = self.clean_text(text_b)

        if not cleaned_a:
            raise SemanticInputInvalidException(
                "Text A is empty or contains only whitespace.",
                details={"field": "text_a", "input_length": len(text_a or "")},
            )

        if not cleaned_b:
            raise SemanticInputInvalidException(
                "Text B is empty or contains only whitespace.",
                details={"field": "text_b", "input_length": len(text_b or "")},
            )

        if len(cleaned_a) > self.max_length:
            raise SemanticInputInvalidException(
                f"Text A exceeds maximum allowed length ({len(cleaned_a)} > {self.max_length}).",
                details={"field": "text_a", "length": len(cleaned_a), "max_length": self.max_length},
            )

        if len(cleaned_b) > self.max_length:
            raise SemanticInputInvalidException(
                f"Text B exceeds maximum allowed length ({len(cleaned_b)} > {self.max_length}).",
                details={"field": "text_b", "length": len(cleaned_b), "max_length": self.max_length},
            )

        return cleaned_a, cleaned_b

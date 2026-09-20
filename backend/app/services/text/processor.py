"""
Bloop Text Processor Module
Provides pure functions and an object-oriented TextProcessor service for deterministic
text normalization, character counting, word counting, and acoustic metrics derivation.
"""

import re
from typing import Optional
from backend.app.services.text.metrics import TextMetrics

# Regex pattern to match non-printable ASCII control characters while preserving \t (0x09) and \n (0x0A)
_CONTROL_CHAR_REGEX = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def normalize_text(text: Optional[str]) -> str:
    """
    Applies conservative text normalization to input strings.

    Semantics:
    1. None-safe: Converts None to empty string.
    2. Line Ending Normalization: Unifies Windows (CRLF) and legacy Mac (CR) to Unix line feeds (\n).
    3. Control Character Sanitization: Strips non-printable ASCII control codes while preserving
       valid formatting whitespace: horizontal tab (\t) and newline (\n).
    4. Edge Whitespace Stripping: Removes leading and trailing whitespace from the overall string.
    5. Content Integrity: Preserves internal structural whitespace, paragraph spacing,
       punctuation, emojis, and all multilingual Unicode codepoints without semantic rewriting.
    """
    if not text:
        return ""

    # 1. Unify line endings
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Strip non-printable control characters (O(n) pass)
    normalized = _CONTROL_CHAR_REGEX.sub("", normalized)

    # 3. Strip leading and trailing whitespace
    return normalized.strip()


def count_characters(text: str) -> int:
    """
    Authoritative character counting strategy.

    Semantics:
    - Measures exact Unicode string length (len(text)) on the text.
    - Spaces count.
    - Newlines (\\n) count.
    - Tabs (\\t) count.
    - Punctuation marks count.
    - Numbers and symbols count.
    - Multilingual Unicode codepoints count as individual Python string characters.
    """
    return len(text)


def count_words(text: str) -> int:
    """
    Authoritative word counting strategy using deterministic whitespace tokenization.

    Semantics:
    - Splits text on continuous sequences of whitespace (spaces, newlines, tabs).
    - Avoids counting leading, trailing, or repeated interstitial whitespace as phantom words.
    - "Hello   Bloop" yields 2 words.
    - "Hello\\nWorld" yields 2 words.
    - Whitespace-only strings yield 0 words.
    """
    if not text:
        return 0
    words = text.split()
    return len(words)


def calculate_metrics(text: str, speaking_rate_wpm: float = 150.0) -> TextMetrics:
    """
    Derives complete TextMetrics from an input string after conservative normalization.

    Args:
        text: Raw input string.
        speaking_rate_wpm: Baseline reading speed in words per minute (default 150.0 WPM).

    Returns:
        Immutable TextMetrics object with normalized text, char count, word count, and duration.
    """
    norm = normalize_text(text)
    chars = count_characters(norm)
    words = count_words(norm)

    # Duration calculation: 150 WPM = 2.5 words/sec. Minimum duration of 0.5s for non-empty text.
    if words > 0:
        words_per_sec = max(speaking_rate_wpm / 60.0, 0.1)
        estimated_duration = round(max(words / words_per_sec, 0.5), 1)
    elif chars > 0:
        # Non-empty characters but 0 words (e.g. punctuation only)
        estimated_duration = 0.5
    else:
        estimated_duration = 0.0

    return TextMetrics(
        character_count=chars,
        word_count=words,
        normalized_text=norm,
        estimated_duration_seconds=estimated_duration,
        speaking_rate_wpm=speaking_rate_wpm,
    )


class TextProcessor:
    """
    Reusable Text Processing Service.
    Encapsulates deterministic text normalization and metrics calculation.
    """

    def __init__(self, default_speaking_rate_wpm: float = 150.0):
        self.default_speaking_rate_wpm = default_speaking_rate_wpm

    def normalize(self, text: Optional[str]) -> str:
        """Normalizes input text conservatively."""
        return normalize_text(text)

    def count_chars(self, text: str) -> int:
        """Counts characters deterministically."""
        return count_characters(text)

    def count_words(self, text: str) -> int:
        """Counts words using whitespace-aware splitting."""
        return count_words(text)

    def analyze(self, text: str, speaking_rate_wpm: Optional[float] = None) -> TextMetrics:
        """Calculates full metrics for an input string."""
        rate = speaking_rate_wpm or self.default_speaking_rate_wpm
        return calculate_metrics(text, speaking_rate_wpm=rate)

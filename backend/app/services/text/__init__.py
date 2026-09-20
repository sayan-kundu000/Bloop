"""
Bloop Text Processing & Validation Domain Package
Exports canonical text processor, validator, metrics, and pure functions.
"""

from backend.app.services.text.metrics import TextMetrics
from backend.app.services.text.processor import (
    TextProcessor,
    calculate_metrics,
    count_characters,
    count_words,
    normalize_text,
)
from backend.app.services.text.validator import TextValidator

__all__ = [
    "TextMetrics",
    "TextProcessor",
    "TextValidator",
    "calculate_metrics",
    "count_characters",
    "count_words",
    "normalize_text",
]

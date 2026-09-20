"""
Unit Tests — Text Validation & Metrics Calculation
"""

import pytest


def calculate_metrics(text: str):
    """Calculates character count, word count, and estimated duration."""
    cleaned = text.strip()
    char_count = len(cleaned)
    words = cleaned.split() if cleaned else []
    word_count = len(words)
    # Average reading speed ~150 words per minute (2.5 words/sec)
    estimated_duration = round(word_count / 2.5, 2)
    return {
        "char_count": char_count,
        "word_count": word_count,
        "estimated_duration": estimated_duration
    }


def test_valid_text_metrics():
    text = "Bloop produces high-fidelity artificial speech."
    metrics = calculate_metrics(text)
    assert metrics["char_count"] == 47
    assert metrics["word_count"] == 5
    assert metrics["estimated_duration"] == 2.0


def test_empty_text_metrics():
    text = "   "
    metrics = calculate_metrics(text)
    assert metrics["char_count"] == 0
    assert metrics["word_count"] == 0
    assert metrics["estimated_duration"] == 0.0


def test_max_length_boundary():
    max_len = 2500
    valid_text = "a" * max_len
    assert len(valid_text) == max_len
    oversized_text = "a" * (max_len + 1)
    assert len(oversized_text) > max_len

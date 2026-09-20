"""
Unit Tests — Text Metrics Object & Duration Calculations
Validates TextMetrics structure, serialization, and duration estimation algorithms.
"""

import pytest
from backend.app.services.text.metrics import TextMetrics
from backend.app.services.text.processor import calculate_metrics


class TestTextMetricsModel:
    """Tests TextMetrics structure and serialization."""

    def test_text_metrics_immutability_and_attributes(self):
        metrics = TextMetrics(
            character_count=42,
            word_count=7,
            normalized_text="Synthesized speech prompt text for metrics.",
            estimated_duration_seconds=2.8,
            speaking_rate_wpm=150.0,
        )
        assert metrics.character_count == 42
        assert metrics.word_count == 7
        assert metrics.estimated_duration_seconds == 2.8
        assert metrics.is_empty is False

        # Verify immutability
        with pytest.raises(Exception):
            metrics.character_count = 50  # type: ignore

    def test_metrics_to_dict_serialization(self):
        metrics = calculate_metrics("Quick test")
        data = metrics.to_dict()
        assert isinstance(data, dict)
        assert data["character_count"] == 10
        assert data["word_count"] == 2
        assert data["normalized_text"] == "Quick test"
        assert "estimated_duration_seconds" in data
        assert "speaking_rate_wpm" in data

    def test_empty_metrics_properties(self):
        empty_metrics = calculate_metrics("    ")
        assert empty_metrics.character_count == 0
        assert empty_metrics.word_count == 0
        assert empty_metrics.is_empty is True
        assert empty_metrics.estimated_duration_seconds == 0.0

    def test_speaking_rate_duration_variations(self):
        # 10 words at 150 WPM = 10 / 2.5 = 4.0 seconds
        text = "one two three four five six seven eight nine ten"
        m150 = calculate_metrics(text, speaking_rate_wpm=150.0)
        assert m150.estimated_duration_seconds == 4.0

        # 10 words at 300 WPM = 10 / 5.0 = 2.0 seconds
        m300 = calculate_metrics(text, speaking_rate_wpm=300.0)
        assert m300.estimated_duration_seconds == 2.0

        # 10 words at 60 WPM = 10 / 1.0 = 10.0 seconds
        m60 = calculate_metrics(text, speaking_rate_wpm=60.0)
        assert m60.estimated_duration_seconds == 10.0

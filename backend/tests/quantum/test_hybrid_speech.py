"""
Tests for Hybrid Speech Intelligence, Acoustic Recommendations, and Voice Decoupling
Verifies provider-independent recommendation mapping, dynamic voice capability checks,
and total decoupling from ElevenLabs.
"""

import pytest

from backend.app.quantum.hybrid.recommendation import HybridSpeechRecommender
from backend.app.quantum.hybrid.speech_bridge import SpeechCapabilityBridge
from backend.app.quantum.hybrid.models import SpeechRecommendationDTO


def test_speech_recommendation_joy():
    """Verifies that positive/joy sentiment maps to expressive acoustic parameters."""
    recommender = HybridSpeechRecommender()
    rec = recommender.generate_recommendation(
        predicted_class="joy",
        class_scores={"joy": 0.85, "neutral": 0.15},
        confidence=0.85,
    )

    assert rec.style == "expressive"
    assert rec.speed > 1.0
    assert rec.pitch > 1.0
    assert rec.stability == 0.50
    assert rec.pacing == "dynamic"
    assert rec.applied is False
    assert "positive" in rec.reason.lower() or "joy" in rec.reason.lower()


def test_speech_recommendation_sadness():
    """Verifies that somber/sadness sentiment maps to subdued acoustic parameters."""
    recommender = HybridSpeechRecommender()
    rec = recommender.generate_recommendation(
        predicted_class="sadness",
        class_scores={"sadness": 0.80, "neutral": 0.20},
        confidence=0.80,
    )

    assert rec.style == "subdued"
    assert rec.speed < 1.0
    assert rec.pitch < 1.0
    assert rec.stability == 0.75
    assert rec.pacing == "slow"


def test_speech_recommendation_anger():
    """Verifies that assertive/anger sentiment maps to intense delivery."""
    recommender = HybridSpeechRecommender()
    rec = recommender.generate_recommendation(
        predicted_class="anger",
        class_scores={"anger": 0.90, "neutral": 0.10},
        confidence=0.90,
    )

    assert rec.style == "intense"
    assert rec.speed >= 1.10
    assert rec.pacing == "fast"


def test_speech_recommendation_ambiguous_fallback():
    """Verifies that low-confidence or ambiguous classifications fallback to conservative defaults."""
    recommender = HybridSpeechRecommender()
    rec = recommender.generate_recommendation(
        predicted_class="joy",
        class_scores={"joy": 0.25, "sadness": 0.25, "neutral": 0.50},
        confidence=0.25,  # Below threshold 0.35
    )

    assert rec.style == "balanced"
    assert rec.speed == 1.0
    assert rec.pitch == 1.0
    assert rec.stability == 0.65
    assert rec.confidence is None
    assert "ambiguous" in rec.reason.lower()


def test_speech_bridge_tts_payload_formatting():
    """Verifies that SpeechCapabilityBridge formats canonical TTSRequest payloads without calling providers."""
    rec = SpeechRecommendationDTO(
        style="expressive",
        speed=1.08,
        pitch=1.05,
        stability=0.50,
        similarity_boost=0.80,
        pacing="dynamic",
        reason="Joy detected",
        applied=False,
    )

    payload = SpeechCapabilityBridge.format_tts_payload(
        text="Hello world",
        recommendation=rec,
        voice_id="voice-rachel-123",
        language="en-US",
    )

    assert payload["text"] == "Hello world"
    assert payload["voice_id"] == "voice-rachel-123"
    assert payload["speed"] == 1.08
    assert payload["pitch"] == 1.05
    assert payload["settings"]["stability"] == 0.50
    assert payload["settings"]["similarity_boost"] == 0.80


def test_elevenlabs_isolation_in_hybrid():
    """
    Architectural Decoupling Check:
    Verifies that the hybrid recommendation layer does NOT import or reference ElevenLabs.
    """
    import inspect
    import backend.app.quantum.hybrid.recommendation as rec_module
    import backend.app.quantum.hybrid.speech_bridge as bridge_module

    rec_source = inspect.getsource(rec_module)
    bridge_source = inspect.getsource(bridge_module)

    assert "elevenlabs_provider" not in rec_source.lower()
    assert "elevenlabsprovider" not in rec_source.lower()
    assert "import elevenlabs" not in rec_source.lower()
    assert "elevenlabs_provider" not in bridge_source.lower()
    assert "elevenlabsprovider" not in bridge_source.lower()
    assert "import elevenlabs" not in bridge_source.lower()

"""
API Integration Tests for POST /api/v1/quantum/emotion
Verifies: authentication, prompt validation, resource limits, speech recommendations,
backwards compatibility, and multi-tenant experiment history persistence.
"""

import pytest
from backend.app.api.deps import get_current_user
from backend.app.core.config import settings
from backend.app.main import app
from backend.app.models.user import User


@pytest.fixture
def auth_user():
    user = User(id=42, email="emotion_researcher@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.pop(get_current_user, None)


def test_quantum_emotion_unauthenticated(client):
    app.dependency_overrides.pop(get_current_user, None)
    res = client.post(
        "/api/v1/quantum/emotion",
        json={"text": "Testing unauthenticated access rejection."},
    )
    assert res.status_code == 401


def test_quantum_emotion_valid_prompt_24_request(client, auth_user):
    payload = {
        "text": "I am so joyful and thrilled with this tremendous accomplishment!",
        "shots": 512,
        "num_qubits": 4,
        "circuit_depth": 4,
        "framework": "pennylane",
        "include_recommendation": True,
    }
    res = client.post("/api/v1/quantum/emotion", json=payload)
    assert res.status_code == 200

    data = res.json()["data"]
    assert data["detected_emotion"] in ["joy", "sadness", "anger", "neutral"]
    assert "emotion_scores" in data
    assert len(data["emotion_scores"]) == 4
    assert data["entanglement_entropy"] >= 0.0
    assert data["circuit_depth"] > 0
    assert data["num_qubits"] == 4
    assert data["execution_time_ms"] > 0

    # Prompt 24 Speech Recommendation verification
    assert data["speech_recommendation"] is not None
    rec = data["speech_recommendation"]
    assert "style" in rec
    assert "speed" in rec
    assert "pitch" in rec
    assert "stability" in rec
    assert "similarity_boost" in rec
    assert "pacing" in rec
    assert "reason" in rec
    assert rec["applied"] is False  # User must explicitly choose to apply

    # Legacy backward-compatible fields
    assert "quantum_probabilities" in data
    assert "classical_baseline_emotion" in data


def test_quantum_emotion_disabled_recommendation(client, auth_user):
    payload = {
        "text": "Standard system operation completed routine database update.",
        "include_recommendation": False,
    }
    res = client.post("/api/v1/quantum/emotion", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["speech_recommendation"] is None


def test_quantum_emotion_empty_input_rejection(client, auth_user):
    res = client.post("/api/v1/quantum/emotion", json={"text": ""})
    assert res.status_code in [422, 400]

    res_ws = client.post("/api/v1/quantum/emotion", json={"text": "   \n\t   "})
    assert res_ws.status_code in [422, 400]


def test_quantum_emotion_too_long_rejection(client, auth_user):
    oversized = "x" * 1005
    res = client.post("/api/v1/quantum/emotion", json={"text": oversized})
    assert res.status_code in [422, 400]


def test_quantum_emotion_disabled_mode_safeguard(client, auth_user, monkeypatch):
    monkeypatch.setattr(settings, "QUANTUM_ENABLED", False)
    res = client.post(
        "/api/v1/quantum/emotion",
        json={"text": "System text during maintenance mode."},
    )
    assert res.status_code == 503
    assert res.json()["error"]["code"] == "QUANTUM_DISABLED"


def test_quantum_emotion_history_persistence(client, auth_user):
    # Perform analysis
    client.post(
        "/api/v1/quantum/emotion",
        json={"text": "Heartbreaking news left us in deep sadness and lonely grief."},
    )

    # Query history
    res = client.get("/api/v1/quantum/history?experiment_type=emotion")
    assert res.status_code == 200
    items = res.json()["data"]
    assert len(items) >= 1
    assert items[0]["type"] == "emotion"

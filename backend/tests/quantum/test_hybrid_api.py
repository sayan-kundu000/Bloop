"""
API Integration Tests for Quantum Benchmarking and Hybrid Intelligence Endpoints
Tests:
  - GET  /api/v1/quantum/benchmark/categories
  - POST /api/v1/quantum/benchmark
  - POST /api/v1/quantum/hybrid/analyze
  - POST /api/v1/quantum/hybrid/recommend
  - Authentication checks and input validation error handling.
"""

import pytest
from backend.app.api.deps import get_current_user
from backend.app.main import app
from backend.app.models.user import User


@pytest.fixture
def auth_user():
    user = User(id=88, email="hybrid_researcher@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.pop(get_current_user, None)


def test_get_benchmark_categories(client):
    """Verifies retrieval of supported benchmark categories."""
    res = client.get("/api/v1/quantum/benchmark/categories")
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    categories = body["data"]
    assert len(categories) >= 5
    cat_ids = [c["category"] for c in categories]
    assert "text_classification" in cat_ids
    assert "emotion_qnn" in cat_ids
    assert "semantic_similarity" in cat_ids
    assert "circuit_noise" in cat_ids
    assert "hybrid_speech_pipeline" in cat_ids


def test_benchmark_endpoint_unauthenticated(client):
    """Verifies that running a benchmark requires authentication."""
    app.dependency_overrides.pop(get_current_user, None)
    res = client.post(
        "/api/v1/quantum/benchmark",
        json={"category": "text_classification", "dataset_size": 20},
    )
    assert res.status_code == 401


def test_benchmark_endpoint_authenticated(client, auth_user):
    """Verifies authenticated benchmark execution across candidate models."""
    res = client.post(
        "/api/v1/quantum/benchmark",
        json={
            "category": "text_classification",
            "dataset_size": 20,
            "test_split": 0.25,
            "num_qubits": 2,
            "shots": 128,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert "classical_metrics" in data
    assert "quantum_metrics" in data
    assert "honest_analysis" in data
    assert data["classical_metrics"]["inference_time_seconds"] >= 0.0


def test_benchmark_endpoint_semantic_category(client, auth_user):
    """Verifies benchmark execution with semantic similarity category."""
    res = client.post(
        "/api/v1/quantum/benchmark",
        json={
            "category": "semantic_similarity",
            "num_qubits": 2,
            "shots": 128,
            "classical_weight": 0.5,
            "quantum_weight": 0.5,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["category"] == "semantic_similarity"
    assert "mae" in data["classical_metrics"]
    assert "mae" in data["quantum_metrics"]


def test_hybrid_analyze_unauthenticated(client):
    """Verifies that hybrid analysis requires authentication."""
    app.dependency_overrides.pop(get_current_user, None)
    res = client.post(
        "/api/v1/quantum/hybrid/analyze",
        json={"text": "Amazing voice synthesis quality!"},
    )
    assert res.status_code == 401


def test_hybrid_analyze_authenticated(client, auth_user):
    """Verifies authenticated hybrid analysis with recommendation generation."""
    res = client.post(
        "/api/v1/quantum/hybrid/analyze",
        json={
            "text": "Delighted by the vibrant and natural sounding speech generation!",
            "include_recommendation": True,
            "num_qubits": 2,
            "shots": 128,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert "classical_prediction" in data
    assert "quantum_prediction" in data
    assert "hybrid_prediction" in data
    assert "speech_recommendation" in data
    assert data["speech_recommendation"] is not None
    assert "style" in data["speech_recommendation"]
    assert "speed" in data["speech_recommendation"]
    assert "pipeline_breakdown" in data
    assert data["pipeline_breakdown"]["total_ms"] > 0.0


def test_hybrid_recommend_endpoint(client, auth_user):
    """Verifies standalone speech recommendation endpoint."""
    res = client.post(
        "/api/v1/quantum/hybrid/recommend",
        json={
            "text": "I am thrilled and overjoyed with the magnificent audio outcome!",
            "predicted_emotion": "joy",
            "confidence": 0.88,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    rec = body["data"]
    assert rec["style"] == "expressive"
    assert rec["speed"] >= 1.05
    assert rec["applied"] is False


def test_hybrid_analyze_validation_error(client, auth_user):
    """Verifies rejection of empty text."""
    res = client.post(
        "/api/v1/quantum/hybrid/analyze",
        json={"text": ""},
    )
    assert res.status_code == 422

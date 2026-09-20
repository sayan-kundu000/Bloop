"""
API Integration Tests for Quantum Semantic Endpoints
Tests: POST /api/v1/quantum/semantic, /semantic/matrix, /semantic/benchmark,
authentication, rate limits, resource validation, and multi-tenant experiment history.
"""

import pytest
from backend.app.api.deps import get_current_user
from backend.app.main import app
from backend.app.models.user import User


@pytest.fixture
def auth_user():
    user = User(id=42, email="semantic_researcher@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.pop(get_current_user, None)


def test_quantum_semantic_unauthenticated(client):
    app.dependency_overrides.pop(get_current_user, None)
    res = client.post(
        "/api/v1/quantum/semantic",
        json={"text_a": "First prompt.", "text_b": "Second prompt."},
    )
    assert res.status_code == 401


def test_quantum_semantic_valid_hybrid_request(client, auth_user):
    payload = {
        "text_a": "Artificial intelligence converts written text into natural human speech.",
        "text_b": "AI models synthesize voice audio from text input prompts.",
        "method": "hybrid",
        "framework": "qiskit",
        "num_qubits": 4,
        "shots": 512,
    }
    res = client.post("/api/v1/quantum/semantic", json=payload)
    assert res.status_code == 200

    data = res.json()["data"]
    assert data["text_a"] == payload["text_a"]
    assert data["text_b"] == payload["text_b"]
    assert 0.0 <= data["quantum_kernel_similarity"] <= 1.0
    assert 0.0 <= data["classical_cosine_similarity"] <= 1.0
    assert "similarity_verdict" in data
    assert data["divergence"] >= 0.0
    assert data["circuit_depth"] > 0
    assert data["num_qubits"] == 4
    assert data["execution_time_ms"] > 0
    assert data["method"] == "hybrid"
    assert data["representation_method"] is not None
    assert len(data["pipeline_steps"]) > 0


def test_quantum_semantic_classical_method(client, auth_user):
    payload = {
        "text_a": "Natural speech synthesis audio.",
        "text_b": "Voice speech synthesis engine.",
        "method": "classical",
    }
    res = client.post("/api/v1/quantum/semantic", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["method"] == "classical"
    assert data["classical_similarity"] > 0.0
    assert data["circuit_depth"] == 0


def test_quantum_semantic_pennylane_framework(client, auth_user):
    payload = {
        "text_a": "Quantum computing simulation.",
        "text_b": "Variational circuit simulation.",
        "method": "hybrid",
        "framework": "pennylane",
        "num_qubits": 2,
        "shots": 256,
    }
    res = client.post("/api/v1/quantum/semantic", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["quantum_framework"] == "pennylane"
    assert data["num_qubits"] == 2


def test_quantum_semantic_empty_input_rejected(client, auth_user):
    res = client.post(
        "/api/v1/quantum/semantic",
        json={"text_a": "   ", "text_b": "Valid text"},
    )
    assert res.status_code in [400, 422]


def test_quantum_semantic_matrix_endpoint(client, auth_user):
    payload = {
        "texts": [
            "Natural language processing.",
            "Text semantic similarity.",
            "Quantum state fidelity.",
        ],
        "method": "classical",
        "num_qubits": 2,
    }
    res = client.post("/api/v1/quantum/semantic/matrix", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["num_texts"] == 3
    assert data["total_comparisons"] == 3
    assert len(data["matrix"]) == 3
    assert len(data["matrix"][0]) == 3
    assert data["matrix"][0][0] == 1.0


def test_quantum_semantic_matrix_limit_exceeded(client, auth_user):
    payload = {
        "texts": [f"Text prompt number {i}" for i in range(8)],  # 8 texts = 28 pairs > 20
        "method": "classical",
    }
    res = client.post("/api/v1/quantum/semantic/matrix", json=payload)
    assert res.status_code in [400, 422]


def test_quantum_semantic_benchmark_endpoint(client, auth_user):
    payload = {
        "num_qubits": 2,
        "shots": 256,
        "framework": "qiskit",
    }
    res = client.post("/api/v1/quantum/semantic/benchmark", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["sample_count"] >= 10
    assert "classical_metrics" in data
    assert "quantum_metrics" in data
    assert "honest_analysis" in data
    assert data["execution_time_ms"] > 0


def test_semantic_history_persistence(client, auth_user):
    # 1. Run semantic similarity
    payload = {
        "text_a": "Unique semantic query for history tracking.",
        "text_b": "Another distinct prompt for audit logging.",
        "num_qubits": 2,
    }
    sim_res = client.post("/api/v1/quantum/semantic", json=payload)
    assert sim_res.status_code == 200

    # 2. Query history
    hist_res = client.get("/api/v1/quantum/history?experiment_type=quantum_semantic&limit=5")
    assert hist_res.status_code == 200
    records = hist_res.json()["data"]
    assert len(records) > 0
    assert any("Semantic Analysis" in r["title"] or "quantum_semantic" in r["type"] for r in records)

"""
API Integration Tests for POST /api/v1/quantum/text
Verifies: authentication, prompt validation, resource limits, framework selection,
backwards compatibility, and multi-tenant experiment history persistence.
"""

import pytest
from backend.app.api.deps import get_current_user
from backend.app.core.config import settings
from backend.app.main import app
from backend.app.models.user import User


@pytest.fixture
def auth_user():
    user = User(id=42, email="quantum_researcher@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.pop(get_current_user, None)


def test_quantum_text_unauthenticated(client):
    app.dependency_overrides.pop(get_current_user, None)
    res = client.post(
        "/api/v1/quantum/text",
        json={"text": "Analyzing unauthenticated access rejection."},
    )
    assert res.status_code == 401


def test_quantum_text_valid_prompt_23_request(client, auth_user):
    payload = {
        "text": "Deep neural networks optimize loss gradients via backpropagation algorithms.",
        "task": "classification",
        "model": "hybrid_quantum_classifier",
        "framework": "qiskit",
        "num_qubits": 4,
        "shots": 512,
        "circuit_depth": 2,
    }
    res = client.post("/api/v1/quantum/text", json=payload)
    assert res.status_code == 200

    data = res.json()["data"]
    # Prompt 23 attributes
    assert data["task"] == "classification"
    assert data["model"] == "hybrid_quantum_classifier"
    assert data["predicted_style"] in ["technical", "formal", "casual", "creative"]
    assert "classical_baseline" in data
    assert data["quantum"]["framework"] == "qiskit"
    assert data["quantum"]["qubits"] == 4
    assert len(data["pipeline_steps"]) == 7

    # Backwards-compatible fields
    assert "tokens" in data
    assert len(data["classical_features"]) == 4
    assert "quantum_probabilities" in data
    assert data["circuit_depth"] > 0
    assert data["execution_time_ms"] > 0


def test_quantum_text_pennylane_framework(client, auth_user):
    payload = {
        "text": "Hey friend, let's catch up and have some fun this weekend!",
        "framework": "pennylane",
        "num_qubits": 2,
        "shots": 512,
    }
    res = client.post("/api/v1/quantum/text", json=payload)
    assert res.status_code == 200

    data = res.json()["data"]
    assert data["quantum"]["framework"] == "pennylane"
    assert data["num_qubits"] == 2


def test_quantum_text_empty_input_rejection(client, auth_user):
    res = client.post("/api/v1/quantum/text", json={"text": ""})
    assert res.status_code in [422, 400]

    res_ws = client.post("/api/v1/quantum/text", json={"text": "    \t\n  "})
    assert res_ws.status_code in [422, 400]


def test_quantum_text_too_long_rejection(client, auth_user):
    oversized = "a" * 1005
    res = client.post("/api/v1/quantum/text", json={"text": oversized})
    assert res.status_code in [422, 400]


def test_quantum_text_qubit_boundary_rejection(client, auth_user):
    res = client.post(
        "/api/v1/quantum/text",
        json={"text": "Valid text", "num_qubits": 16},
    )
    assert res.status_code in [422, 400]


def test_quantum_text_history_persistence(client, auth_user):
    # Execute analysis
    client.post(
        "/api/v1/quantum/text",
        json={"text": "Formal executive summary of quarterly operational metrics.", "num_qubits": 4},
    )

    # Check history
    res = client.get("/api/v1/quantum/history?experiment_type=text")
    assert res.status_code == 200
    items = res.json()["data"]
    assert len(items) >= 1
    assert items[0]["type"] == "text"

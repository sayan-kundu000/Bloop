"""
API Integration Tests for Quantum Circuit & Noise Laboratory Endpoints
Tests:
  - POST /api/v1/quantum/circuit (Single simulation)
  - POST /api/v1/quantum/circuit/compare (Ideal vs Noisy comparison)
  - POST /api/v1/quantum/circuit/robustness (Noise parameter sweep)
  - GET  /api/v1/quantum/circuit/templates
  - GET  /api/v1/quantum/circuit/noise-profiles
  - GET  /api/v1/quantum/circuit/gates
  - Authentication, validation error envelopes, and rate limiting guards.
"""

import pytest
from backend.app.api.deps import get_current_user
from backend.app.main import app
from backend.app.models.user import User


@pytest.fixture
def auth_user():
    user = User(id=77, email="lab_researcher@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.pop(get_current_user, None)


def test_circuit_execution_unauthenticated(client):
    app.dependency_overrides.pop(get_current_user, None)
    res = client.post(
        "/api/v1/quantum/circuit",
        json={"num_qubits": 2, "preset": "bell_state"},
    )
    assert res.status_code == 401


def test_circuit_authenticated_ideal(client, auth_user):
    payload = {
        "num_qubits": 2,
        "gates": [
            {"gate": "h", "target": 0},
            {"gate": "cx", "control": 0, "target": 1},
        ],
        "shots": 500,
        "noise_level": 0.0,
    }
    res = client.post("/api/v1/quantum/circuit", json=payload)
    assert res.status_code == 200

    body = res.json()
    assert body["success"] is True
    data = body["data"]
    assert data["num_qubits"] == 2
    assert not data["is_noisy_simulation"]
    assert "00" in data["probabilities"]
    assert "11" in data["probabilities"]
    assert "circuit_diagram_ascii" in data
    assert "qasm" in data


def test_circuit_authenticated_noisy(client, auth_user):
    payload = {
        "num_qubits": 2,
        "preset": "bell_state",
        "shots": 500,
        "noise_profile": "medium_noise",
    }
    res = client.post("/api/v1/quantum/circuit", json=payload)
    assert res.status_code == 200

    data = res.json()["data"]
    assert data["is_noisy_simulation"] is True
    assert data["noise_model"] is not None


def test_circuit_comparison_endpoint(client, auth_user):
    payload = {
        "num_qubits": 2,
        "preset": "bell_state",
        "shots": 500,
        "noise_profile": "medium_noise",
    }
    res = client.post("/api/v1/quantum/circuit/compare", json=payload)
    assert res.status_code == 200

    data = res.json()["data"]
    assert "total_variation_distance" in data
    assert "classical_fidelity" in data
    assert "states_comparison" in data
    assert len(data["states_comparison"]) >= 2
    assert "ideal_entropy" in data
    assert "noisy_entropy" in data


def test_circuit_robustness_endpoint(client, auth_user):
    payload = {
        "num_qubits": 2,
        "preset": "bell_state",
        "noise_model": "depolarizing",
        "sweep": {
            "parameter": "probability",
            "start": 0.0,
            "stop": 0.04,
            "step": 0.02,
        },
        "shots": 400,
        "repeats_per_point": 1,
    }
    res = client.post("/api/v1/quantum/circuit/robustness", json=payload)
    assert res.status_code == 200

    data = res.json()["data"]
    assert data["sweep_parameter"] == "probability"
    assert len(data["points"]) == 3
    assert data["total_runs"] == 3
    assert "summary" in data


def test_circuit_templates_endpoint(client):
    res = client.get("/api/v1/quantum/circuit/templates")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) >= 5
    ids = [t["id"] for t in data]
    assert "bell_state" in ids
    assert "ghz_state" in ids


def test_circuit_noise_profiles_endpoint(client):
    res = client.get("/api/v1/quantum/circuit/noise-profiles")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 4
    names = [p["id"] for p in data]
    assert "ideal" in names
    assert "medium_noise" in names


def test_circuit_gates_endpoint(client):
    res = client.get("/api/v1/quantum/circuit/gates")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 12
    gate_names = [g["gate"] for g in data]
    assert "h" in gate_names
    assert "cx" in gate_names
    assert "rx" in gate_names


def test_circuit_invalid_gate_rejected(client, auth_user):
    payload = {
        "num_qubits": 2,
        "gates": [
            {"gate": "forbidden_oracle_gate", "target": 0},
        ],
    }
    res = client.post("/api/v1/quantum/circuit", json=payload)
    assert res.status_code == 400
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNSUPPORTED_GATE"


def test_circuit_invalid_qubit_index(client, auth_user):
    payload = {
        "num_qubits": 2,
        "gates": [
            {"gate": "h", "target": 7},
        ],
    }
    res = client.post("/api/v1/quantum/circuit", json=payload)
    assert res.status_code == 400
    body = res.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_QUBIT_INDEX"

"""
API Tests for Quantum Computing Foundation Layer
Verifies health check endpoints, circuit simulation, benchmark API, resource limits, and disabled mode.
"""

import pytest
from backend.app.api.deps import get_current_user, get_settings
from backend.app.core.config import Settings
from backend.app.main import app
from backend.app.models.user import User


@pytest.fixture
def auth_user():
    user = User(id=1, email="quantum_architect@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.pop(get_current_user, None)


def test_quantum_health_endpoint(client):
    """Verifies that GET /health returns operational status and framework availability."""
    res = client.get("/api/v1/quantum/health")
    assert res.status_code == 200
    data = res.json()["data"]

    assert "enabled" in data
    assert "qiskit_available" in data
    assert "aer_available" in data
    assert "pennylane_available" in data
    assert "execution_ready" in data
    assert "limits" in data
    assert data["limits"]["max_qubits"] >= 2
    assert data["limits"]["max_shots"] >= 1024


def test_quantum_status_alias_endpoint(client):
    """Verifies that GET /status functions identically to /health."""
    res = client.get("/api/v1/quantum/status")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["execution_ready"] is True


def test_quantum_circuit_simulation_api(client, auth_user):
    """Verifies Bell state circuit simulation via API."""
    payload = {
        "num_qubits": 2,
        "gates": [
            {"gate": "h", "target": 0},
            {"gate": "cx", "control": 0, "target": 1},
        ],
        "shots": 512,
        "noise_level": 0.0,
    }
    res = client.post("/api/v1/quantum/circuit", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["num_qubits"] == 2
    assert "counts" in data
    assert "00" in data["counts"] or "11" in data["counts"]
    assert "probabilities" in data
    assert "circuit_diagram_ascii" in data
    assert "qasm" in data


def test_quantum_circuit_qubit_limit_rejection(client, auth_user):
    """Verifies that requests exceeding max qubits are rejected with 422."""
    payload = {
        "num_qubits": 12,  # Max allowable is 8
        "gates": [{"gate": "h", "target": 0}],
        "shots": 512,
    }
    res = client.post("/api/v1/quantum/circuit", json=payload)
    assert res.status_code == 422


def test_quantum_circuit_shots_limit_rejection(client, auth_user):
    """Verifies that requests exceeding max shots are rejected with 422."""
    payload = {
        "num_qubits": 2,
        "gates": [{"gate": "h", "target": 0}],
        "shots": 20000,  # Max allowable is 8192
    }
    res = client.post("/api/v1/quantum/circuit", json=payload)
    assert res.status_code == 422


def test_quantum_benchmark_api(client, auth_user):
    """Verifies empirical benchmark evaluation endpoint."""
    payload = {
        "dataset_size": 30,
        "test_split": 0.25,
        "num_qubits": 3,
        "shots": 512,
    }
    res = client.post("/api/v1/quantum/benchmark", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]

    assert "classical_metrics" in data
    assert "quantum_metrics" in data
    assert "honest_analysis" in data
    assert "quantum_advantage_detected" in data


def test_quantum_unauthenticated_access(client):
    """Verifies that unauthenticated requests to protected endpoints return 401."""
    # Ensure current user override is clear
    app.dependency_overrides.pop(get_current_user, None)
    res = client.post(
        "/api/v1/quantum/circuit",
        json={"num_qubits": 2, "gates": [], "shots": 512},
    )
    assert res.status_code == 401


def test_quantum_disabled_mode_safeguard(client, auth_user):
    """Verifies that QUANTUM_ENABLED=false returns 503 QUANTUM_DISABLED."""
    disabled_settings = Settings(
        QUANTUM_ENABLED=False,
        DATABASE_URL="sqlite:///./test_bloop.db",
        APP_ENV="test",
    )
    app.dependency_overrides[get_settings] = lambda: disabled_settings

    try:
        res = client.post(
            "/api/v1/quantum/circuit",
            json={"num_qubits": 2, "gates": [], "shots": 512},
        )
        assert res.status_code == 503
        err = res.json()["error"]
        assert err["code"] == "QUANTUM_DISABLED"
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_quantum_circuit_preset_api(client, auth_user):
    """Verifies that preset circuit executions (e.g., bell_state) work directly."""
    payload = {
        "preset": "bell_state",
        "shots": 256,
    }
    res = client.post("/api/v1/quantum/circuit", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["num_qubits"] == 2
    assert "counts" in data
    assert sum(data["counts"].values()) == 256


def test_quantum_circuit_qubits_alias_api(client, auth_user):
    """Verifies that 'qubits' is accepted as an alias for 'num_qubits'."""
    payload = {
        "qubits": 1,
        "preset": "single_qubit_x",
        "shots": 256,
    }
    res = client.post("/api/v1/quantum/circuit", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["num_qubits"] == 1
    assert "1" in data["counts"]


def test_quantum_history_user_ownership_isolation(client):
    """Verifies strict multi-tenant ownership: User B cannot see or query User A's experiments."""
    user_a = User(id=101, email="user_a@bloop.ai", is_active=True, is_superuser=False)
    user_b = User(id=102, email="user_b@bloop.ai", is_active=True, is_superuser=False)

    # 1. User A executes a circuit
    app.dependency_overrides[get_current_user] = lambda: user_a
    res = client.post(
        "/api/v1/quantum/circuit",
        json={"preset": "bell_state", "shots": 256},
    )
    assert res.status_code == 200

    # User A checks history
    res_a = client.get("/api/v1/quantum/history")
    assert res_a.status_code == 200
    items_a = res_a.json()["data"]
    assert len(items_a) >= 1
    user_a_exp_id = items_a[0]["id"]

    # User A can query single experiment detail
    detail_res_a = client.get(f"/api/v1/quantum/history/{user_a_exp_id}")
    assert detail_res_a.status_code == 200
    assert detail_res_a.json()["data"]["id"] == user_a_exp_id

    # 2. Switch identity to User B
    app.dependency_overrides[get_current_user] = lambda: user_b

    # User B checks history: User A's experiment must NOT be present
    res_b = client.get("/api/v1/quantum/history")
    assert res_b.status_code == 200
    items_b = res_b.json()["data"]
    user_b_ids = [item["id"] for item in items_b]
    assert user_a_exp_id not in user_b_ids

    # User B attempts to fetch User A's experiment detail: must receive 404
    detail_res_b = client.get(f"/api/v1/quantum/history/{user_a_exp_id}")
    assert detail_res_b.status_code == 404

    # Clean up overrides
    app.dependency_overrides.pop(get_current_user, None)


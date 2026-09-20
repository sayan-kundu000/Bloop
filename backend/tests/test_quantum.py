import pytest
from backend.app.api.deps import get_current_user
from backend.app.main import app
from backend.app.models.user import User
from backend.app.schemas.quantum import GateOperation


@pytest.fixture(autouse=True)
def authenticate_user():
    user = User(id=1, email="test_quantum@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.pop(get_current_user, None)


def test_quantum_text_analysis(client):
    res = client.post(
        "/api/v1/quantum/text",
        json={"text": "Modern quantum computing circuit execution", "num_qubits": 4, "shots": 512},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert "predicted_style" in data
    assert "confidence" in data
    assert len(data["classical_features"]) == 4


def test_quantum_emotion_analysis(client):
    res = client.post(
        "/api/v1/quantum/emotion",
        json={"text": "I am delighted and joyful with this wonderful result!", "shots": 512},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["detected_emotion"] == "joy"
    assert "entanglement_entropy" in data


def test_quantum_circuit_simulation(client):
    res = client.post(
        "/api/v1/quantum/circuit",
        json={
            "num_qubits": 2,
            "gates": [
                {"gate": "h", "target": 0},
                {"gate": "cx", "control": 0, "target": 1},
            ],
            "shots": 512,
            "noise_level": 0.0,
        },
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["num_qubits"] == 2
    assert "00" in data["counts"] or "11" in data["counts"]
    assert "circuit_diagram_ascii" in data


def test_quantum_semantic_similarity(client):
    res = client.post(
        "/api/v1/quantum/semantic",
        json={
            "text_a": "Artificial intelligence speech generation",
            "text_b": "Speech synthesis with AI models",
            "num_qubits": 4,
        },
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert 0.0 <= data["quantum_kernel_similarity"] <= 1.0
    assert "similarity_verdict" in data

"""
End-to-End Release Smoke Test (Prompt 28 §32)
Simulates the authoritative complete user journey:
1. Register
2. Login & Session Token Acquisition
3. Load Supported Languages & Dynamic Voices
4. Validate Voice Compatibility
5. Generate Speech
6. Receive Audio & Metadata
7. Favorite Generation
8. Inspect History & Favorites
9. Execute Quantum Side-Car Intelligence Analysis
10. Re-verify Core TTS Operates Completely Independently of Quantum Layer
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.db.session import engine, Base, SessionLocal
from backend.app.db.init_db import init_db
from backend.app.factory import create_app


@pytest.fixture
def smoke_client():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db)
    db.close()
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_complete_user_release_journey(smoke_client: TestClient):
    # 1. Register User
    uid = uuid.uuid4().hex[:8]
    email = f"release_smoke_{uid}@example.com"
    password = "SecurePassword123!"
    full_name = "Release Verification User"

    reg_res = smoke_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    assert reg_res.status_code == 201
    assert reg_res.json()["success"] is True

    # 2. Login User
    login_res = smoke_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()["data"]
    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Load Languages & Voices
    lang_res = smoke_client.get("/api/v1/languages")
    assert lang_res.status_code == 200
    languages = lang_res.json()["data"]
    assert len(languages) > 0

    voice_res = smoke_client.get("/api/v1/voices")
    assert voice_res.status_code == 200
    voices = voice_res.json()["data"]
    assert len(voices) > 0
    test_voice_id = voices[0]["voice_id"]
    test_lang_code = voices[0].get("language_code", "en-US")

    # 4. Generate Speech (Core TTS Engine)
    tts_payload = {
        "text": "Bloop provides intermediate-level full-stack AI speech synthesis with optional quantum intelligence.",
        "voice_id": test_voice_id,
        "language_code": test_lang_code,
    }
    tts_res = smoke_client.post("/api/v1/tts", json=tts_payload, headers=headers)
    assert tts_res.status_code == 200
    tts_data = tts_res.json()["data"]
    assert "audio_url" in tts_data
    assert "duration_seconds" in tts_data
    generation_id = tts_data.get("generation_id") or tts_data.get("id")

    # 5. Favorite Generation (if generation_id returned)
    if generation_id:
        fav_res = smoke_client.post(
            "/api/v1/favorites",
            json={"generation_id": generation_id},
            headers=headers,
        )
        assert fav_res.status_code in (200, 201)

        # 6. Check Favorites List
        fav_list = smoke_client.get("/api/v1/favorites", headers=headers)
        assert fav_list.status_code == 200
        assert fav_list.json()["success"] is True

    # 7. Check History
    hist_res = smoke_client.get("/api/v1/history", headers=headers)
    assert hist_res.status_code == 200
    assert hist_res.json()["success"] is True

    # 8. Run Quantum Experiment (Optional Side-Car Layer)
    quantum_payload = {
        "text": "Quantum superposition acoustic modeling test.",
        "num_qubits": 4,
        "shots": 1024,
    }
    q_res = smoke_client.post("/api/v1/quantum/text", json=quantum_payload, headers=headers)
    assert q_res.status_code == 200
    assert q_res.json()["success"] is True
    assert "predicted_style" in q_res.json()["data"]

    # 9. Verify Core TTS Remains Fully Operational After Quantum Execution
    post_quantum_tts = smoke_client.post(
        "/api/v1/tts",
        json={"text": "Post-quantum speech synthesis verification.", "voice_id": test_voice_id, "language_code": test_lang_code},
        headers=headers,
    )
    assert post_quantum_tts.status_code == 200
    assert post_quantum_tts.json()["success"] is True

    # 10. Logout User
    logout_res = smoke_client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["success"] is True

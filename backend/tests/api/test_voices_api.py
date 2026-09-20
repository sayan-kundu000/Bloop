"""
API integration tests for /api/v1/voices endpoints.
Verifies dynamic voice listing, supported_languages array, parameter filtering,
single voice lookup, and provider ID isolation.
"""

from fastapi.testclient import TestClient


def test_get_voices_list_and_supported_languages(client: TestClient):
    response = client.get("/api/v1/voices")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 2

    for voice in body["data"]:
        assert "voice_id" in voice
        assert "name" in voice
        assert "language_code" in voice
        assert "supported_languages" in voice
        assert isinstance(voice["supported_languages"], list)
        assert voice["language_code"] in voice["supported_languages"]
        # CRITICAL: provider_voice_id must never leak to client API responses
        assert "provider_voice_id" not in voice


def test_get_voices_filtering_by_language_and_language_code(client: TestClient):
    # Test via ?language=
    res_lang = client.get("/api/v1/voices?language=en-US")
    assert res_lang.status_code == 200
    body_lang = res_lang.json()
    assert len(body_lang["data"]) >= 2

    # Test via ?language_code=
    res_code = client.get("/api/v1/voices?language_code=en-US")
    assert res_code.status_code == 200
    body_code = res_code.json()
    assert len(body_code["data"]) == len(body_lang["data"])

    # Test with unsupported language returns empty list, not error
    res_empty = client.get("/api/v1/voices?language=non-existent-lang")
    assert res_empty.status_code == 200
    assert res_empty.json()["data"] == []


def test_get_single_voice_by_id(client: TestClient):
    response = client.get("/api/v1/voices/normal-female")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["voice_id"] == "normal-female"
    assert "supported_languages" in body["data"]
    assert "en-US" in body["data"]["supported_languages"]


def test_get_single_voice_not_found(client: TestClient):
    response = client.get("/api/v1/voices/unknown-ghost-voice")
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VOICE_NOT_FOUND"


def test_dynamic_voice_registration_and_immediate_discovery(client: TestClient):
    # Dynamically register a new custom voice
    new_voice_payload = {
        "voice_id": "custom-dynamic-voice-99",
        "name": "Custom Dynamic Voice",
        "language_code": "en-US",
        "gender": "neutral",
        "accent": "Mid-Atlantic",
        "description": "User-registered custom voice identifier.",
        "provider": "dynamic",
    }
    reg_res = client.post("/api/v1/voices", json=new_voice_payload)
    assert reg_res.status_code == 200
    reg_body = reg_res.json()
    assert reg_body["success"] is True
    assert reg_body["data"]["voice_id"] == "custom-dynamic-voice-99"

    # Verify immediate discovery via GET /api/v1/voices
    list_res = client.get("/api/v1/voices")
    assert list_res.status_code == 200
    voice_ids = [v["voice_id"] for v in list_res.json()["data"]]
    assert "custom-dynamic-voice-99" in voice_ids

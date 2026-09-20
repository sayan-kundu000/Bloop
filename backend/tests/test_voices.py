import pytest
from backend.app.api.deps import get_current_user
from backend.app.main import app
from backend.app.models.user import User


@pytest.fixture(autouse=True)
def authenticate_user():
    user = User(id=1, email="test_voices@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.pop(get_current_user, None)


def test_get_all_voices(client):
    res = client.get("/api/v1/voices")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 2
    voice_ids = [v["voice_id"] for v in data]
    assert "normal-male" in voice_ids
    assert "normal-female" in voice_ids


def test_search_voices(client):
    # Search for Female
    res = client.get("/api/v1/voices?search=female")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data) == 1
    assert data[0]["voice_id"] == "normal-female"
    assert "Female" in data[0]["name"]

    # Filter by gender Male
    res2 = client.get("/api/v1/voices?gender=male")
    assert res2.status_code == 200
    data2 = res2.json()["data"]
    assert len(data2) == 1
    assert data2[0]["voice_id"] == "normal-male"
    assert data2[0]["gender"] == "male"

    # Search specifically for "normal male"
    res3 = client.get("/api/v1/voices?search=normal+male")
    assert res3.status_code == 200
    data3 = res3.json()["data"]
    assert len(data3) == 1
    assert data3[0]["voice_id"] == "normal-male"


def test_tts_generation_with_dynamic_voice(client):
    res = client.post(
        "/api/v1/tts",
        json={
            "text": "Welcome to Bloop AI text to speech engine.",
            "language": "en-US",
            "voice_id": "normal-female",
        },
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["voice_id"] == "normal-female"
    assert "audio_url" in data

    audio_res = client.get(data["audio_url"])
    assert audio_res.status_code == 200
    assert len(audio_res.content) > 100

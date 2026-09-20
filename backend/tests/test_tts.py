import pytest
from backend.app.api.deps import get_current_user
from backend.app.main import app
from backend.app.models.user import User


@pytest.fixture(autouse=True)
def authenticate_user():
    user = User(id=1, email="test_tts@bloop.ai", is_active=True, is_superuser=False)
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.pop(get_current_user, None)


def test_tts_analysis(client):
    res = client.post(
        "/api/v1/tts/analyze",
        json={"text": "Hello world from Bloop Text to Speech!"},
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["char_count"] == 38
    assert data["word_count"] == 7
    assert data["is_valid"] is True


def test_tts_validation_empty_text(client):
    res = client.post(
        "/api/v1/tts",
        json={"text": "   ", "language": "en-US", "voice_id": "normal-female"},
    )
    assert res.status_code == 422
    assert res.json()["success"] is False


def test_tts_generation_and_streaming(client):
    sample_text = "Welcome to the Bloop AI speech generation platform."
    gen_res = client.post(
        "/api/v1/tts",
        json={
            "text": sample_text,
            "language": "en-US",
            "voice_id": "normal-female",
        },
    )
    assert gen_res.status_code == 200
    gen_data = gen_res.json()["data"]
    assert "audio_url" in gen_data
    assert gen_data["char_count"] == len(sample_text)
    assert gen_data["provider"] in ["simulation", "elevenlabs"]

    audio_url = gen_data["audio_url"]

    # Stream audio
    audio_res = client.get(audio_url)
    assert audio_res.status_code == 200
    assert len(audio_res.content) > 100
    assert audio_res.headers["content-type"] in ["audio/mpeg", "audio/wav"]


def test_tts_generation_with_emotion(client):
    sample_text = "I am so excited and delighted to try this new feature!"
    gen_res = client.post(
        "/api/v1/tts",
        json={
            "text": sample_text,
            "language": "en-US",
            "voice_id": "normal-female",
            "emotion": "Excited",
        },
    )
    assert gen_res.status_code == 200
    gen_data = gen_res.json()["data"]
    assert gen_data["emotion"] == "Excited"
    assert "audio_url" in gen_data


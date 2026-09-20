"""
Unit Tests for ElevenLabs Low-Level HTTP Client (ElevenLabsClient)
Tests authentication, status code translation, transient retry logic with exponential backoff,
timeout handling, and request correlation.
"""

from unittest.mock import AsyncMock, patch, MagicMock
import httpx
import pytest

from backend.app.providers.elevenlabs.client import ElevenLabsClient
from backend.app.providers.elevenlabs.exceptions import (
    ElevenLabsAuthenticationException,
    ElevenLabsRateLimitException,
    ElevenLabsTimeoutException,
    ElevenLabsUnavailableException,
    ElevenLabsValidationException,
    ElevenLabsVoiceNotFoundException,
)


@pytest.mark.asyncio
async def test_unconfigured_client_raises_authentication_exception():
    """Client must reject synthesis attempts if API key is empty/missing."""
    client = ElevenLabsClient(api_key="")
    assert client.is_configured() is False

    with pytest.raises(ElevenLabsAuthenticationException) as exc_info:
        await client.synthesize(
            voice_id="test-voice-id",
            payload={"text": "Hello world"},
        )
    assert "not configured" in str(exc_info.value)


@pytest.mark.asyncio
async def test_successful_synthesis_returns_audio_and_metadata():
    """Client must return audio bytes and extracted headers upon HTTP 200."""
    client = ElevenLabsClient(api_key="test-secret-key-1234")
    mock_audio = b"\xff\xfb\x90\x44" * 10  # synthetic MP3 frame

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.content = mock_audio
    mock_resp.headers = {
        "content-type": "audio/mpeg",
        "request-id": "el-req-abc-987",
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        audio_bytes, meta = await client.synthesize(
            voice_id="test-voice-id",
            payload={"text": "Testing successful audio synthesis."},
            request_id="bloop-req-456",
        )

        assert audio_bytes == mock_audio
        assert meta["provider_request_id"] == "el-req-abc-987"
        assert meta["content_type"] == "audio/mpeg"
        assert "latency_ms" in meta
        assert meta["latency_ms"] >= 0

        # Verify headers sent
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["headers"]["xi-api-key"] == "test-secret-key-1234"
        assert call_kwargs["headers"]["x-request-id"] == "bloop-req-456"


@pytest.mark.asyncio
async def test_client_error_401_raises_authentication_exception():
    """HTTP 401 must raise ElevenLabsAuthenticationException without retrying."""
    client = ElevenLabsClient(api_key="invalid-key", max_retries=2)

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 401
    mock_resp.headers = {}
    mock_resp.text = '{"detail":{"status":"invalid_api_key"}}'

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        with pytest.raises(ElevenLabsAuthenticationException) as exc_info:
            await client.synthesize(
                voice_id="test-voice-id",
                payload={"text": "Testing 401"},
            )

        # Ensure NO retries were attempted for 401
        assert mock_post.call_count == 1
        assert "authentication failed" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_client_error_404_raises_voice_not_found_exception():
    """HTTP 404 must raise ElevenLabsVoiceNotFoundException without retrying."""
    client = ElevenLabsClient(api_key="valid-key", max_retries=2)

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 404
    mock_resp.headers = {}
    mock_resp.text = '{"detail":{"status":"voice_not_found"}}'

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        with pytest.raises(ElevenLabsVoiceNotFoundException) as exc_info:
            await client.synthesize(
                voice_id="nonexistent-voice-id",
                payload={"text": "Testing 404"},
            )

        assert mock_post.call_count == 1
        assert "nonexistent-voice-id" in str(exc_info.value)


@pytest.mark.asyncio
async def test_client_error_429_raises_rate_limit_exception():
    """HTTP 429 must raise ElevenLabsRateLimitException and extract retry-after."""
    client = ElevenLabsClient(api_key="valid-key", max_retries=2)

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 429
    mock_resp.headers = {"retry-after": "45"}
    mock_resp.text = '{"detail":{"status":"quota_exceeded"}}'

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        with pytest.raises(ElevenLabsRateLimitException) as exc_info:
            await client.synthesize(
                voice_id="test-voice-id",
                payload={"text": "Testing 429"},
            )

        assert mock_post.call_count == 1
        assert exc_info.value.details.get("retry_after_seconds") == 45


@pytest.mark.asyncio
async def test_client_error_422_raises_validation_exception():
    """HTTP 422 must raise ElevenLabsValidationException."""
    client = ElevenLabsClient(api_key="valid-key", max_retries=2)

    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 422
    mock_resp.headers = {}
    mock_resp.text = '{"detail":{"status":"invalid_payload"}}'

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        with pytest.raises(ElevenLabsValidationException):
            await client.synthesize(
                voice_id="test-voice-id",
                payload={"text": "Testing 422"},
            )

        assert mock_post.call_count == 1


@pytest.mark.asyncio
async def test_transient_503_retries_and_succeeds():
    """HTTP 503 must retry with backoff and succeed if subsequent attempt returns 200."""
    client = ElevenLabsClient(api_key="valid-key", max_retries=2)

    fail_resp = MagicMock(spec=httpx.Response)
    fail_resp.status_code = 503
    fail_resp.headers = {}
    fail_resp.text = "Service Unavailable"

    success_resp = MagicMock(spec=httpx.Response)
    success_resp.status_code = 200
    success_resp.content = b"success-audio"
    success_resp.headers = {"content-type": "audio/mpeg"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        mock_post.side_effect = [fail_resp, success_resp]

        audio_bytes, meta = await client.synthesize(
            voice_id="test-voice-id",
            payload={"text": "Testing retry"},
        )

        assert audio_bytes == b"success-audio"
        assert mock_post.call_count == 2
        mock_sleep.assert_called_once()


@pytest.mark.asyncio
async def test_transient_error_exhausts_retries_and_raises_unavailable():
    """When transient errors persist beyond max_retries, raise ElevenLabsUnavailableException."""
    client = ElevenLabsClient(api_key="valid-key", max_retries=2)

    fail_resp = MagicMock(spec=httpx.Response)
    fail_resp.status_code = 502
    fail_resp.headers = {}
    fail_resp.text = "Bad Gateway"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("asyncio.sleep", new_callable=AsyncMock):
        mock_post.return_value = fail_resp

        with pytest.raises(ElevenLabsUnavailableException) as exc_info:
            await client.synthesize(
                voice_id="test-voice-id",
                payload={"text": "Testing retry exhaustion"},
            )

        assert mock_post.call_count == 3  # 1 initial + 2 retries
        assert "temporarily unavailable" in str(exc_info.value).lower() or "502" in str(exc_info.value)


@pytest.mark.asyncio
async def test_timeout_raises_elevenlabs_timeout_exception():
    """TimeoutException must raise ElevenLabsTimeoutException."""
    client = ElevenLabsClient(api_key="valid-key", max_retries=1, read_timeout=10.0)

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post, \
         patch("asyncio.sleep", new_callable=AsyncMock):
        mock_post.side_effect = httpx.TimeoutException("Read timed out")

        with pytest.raises(ElevenLabsTimeoutException) as exc_info:
            await client.synthesize(
                voice_id="test-voice-id",
                payload={"text": "Testing timeout"},
            )

        assert mock_post.call_count == 2  # 1 initial + 1 retry
        assert exc_info.value.status_code == 504

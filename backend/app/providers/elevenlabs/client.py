"""
ElevenLabs Low-Level HTTP REST Client
Handles secure backend-to-backend communication with ElevenLabs API.
Enforces explicit timeouts, safe transient retry with exponential backoff,
correlation tracking, and status code translation without credential leakage.
"""

import asyncio
import time
from typing import Any, Dict, Optional, Tuple
import httpx

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.elevenlabs.exceptions import (
    ElevenLabsAuthenticationException,
    ElevenLabsException,
    ElevenLabsRateLimitException,
    ElevenLabsTimeoutException,
    ElevenLabsUnavailableException,
    ElevenLabsValidationException,
    ElevenLabsVoiceNotFoundException,
)


class ElevenLabsClient:
    """
    Dedicated HTTPX client adapter for ElevenLabs Text-to-Speech API.
    Isolates external network concerns from the rest of the application.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        connect_timeout: Optional[float] = None,
        read_timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.ELEVENLABS_API_KEY
        self.api_base = (
            api_base or getattr(settings, "ELEVENLABS_API_BASE", "https://api.elevenlabs.io/v1")
        ).rstrip("/")
        self.connect_timeout = (
            connect_timeout
            if connect_timeout is not None
            else getattr(settings, "ELEVENLABS_CONNECT_TIMEOUT_SECONDS", 5.0)
        )
        self.read_timeout = (
            read_timeout
            if read_timeout is not None
            else getattr(settings, "ELEVENLABS_READ_TIMEOUT_SECONDS", 30.0)
        )
        self.max_retries = (
            max_retries
            if max_retries is not None
            else getattr(settings, "ELEVENLABS_MAX_RETRIES", 2)
        )

    def is_configured(self) -> bool:
        """Evaluates whether an ElevenLabs API key is present."""
        return bool(self.api_key and self.api_key.strip())

    async def synthesize(
        self,
        voice_id: str,
        payload: Dict[str, Any],
        output_format: str = "mp3_44100_128",
        request_id: Optional[str] = None,
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Executes a POST request to ElevenLabs /text-to-speech/{voice_id}.
        Retries transient 5xx or network errors with exponential backoff.
        Never retries 4xx client errors (e.g. 401, 404, 422, 429).
        """
        if not self.is_configured():
            logger.error("ElevenLabs API Key is not configured in backend environment.")
            raise ElevenLabsAuthenticationException(
                "ElevenLabs API Key is not configured. Please set ELEVENLABS_API_KEY in your environment."
            )

        url = f"{self.api_base}/text-to-speech/{voice_id}"
        params = {"output_format": output_format}

        headers: Dict[str, str] = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        if request_id:
            headers["x-request-id"] = request_id

        text_length = len(payload.get("text", ""))
        timeout_config = httpx.Timeout(
            connect=self.connect_timeout,
            read=self.read_timeout,
            write=10.0,
            pool=5.0,
        )

        logger.info(
            f"Dispatching ElevenLabs TTS request: voice_id={voice_id}, text_len={text_length}, "
            f"format={output_format}, req_id={request_id or 'none'}"
        )

        attempts = 1 + max(0, self.max_retries)
        last_error: Optional[Exception] = None

        for attempt in range(1, attempts + 1):
            start_time = time.perf_counter()
            try:
                async with httpx.AsyncClient(timeout=timeout_config) as http_client:
                    response = await http_client.post(
                        url,
                        json=payload,
                        params=params,
                        headers=headers,
                    )

                duration_ms = (time.perf_counter() - start_time) * 1000
                resp_headers = getattr(response, "headers", {}) or {}
                provider_req_id = resp_headers.get("request-id") or resp_headers.get("x-request-id")

                # Handle HTTP 200 OK
                if response.status_code == 200:
                    logger.info(
                        f"ElevenLabs synthesis succeeded: voice_id={voice_id}, bytes={len(response.content)}, "
                        f"latency={duration_ms:.1f}ms, provider_req_id={provider_req_id or 'none'}"
                    )
                    metadata = {
                        "provider_request_id": provider_req_id,
                        "content_type": response.headers.get("content-type", "audio/mpeg"),
                        "latency_ms": duration_ms,
                    }
                    return response.content, metadata

                # Handle Non-Retryable Client Errors (4xx)
                if response.status_code == 401:
                    logger.error("ElevenLabs authentication rejected (HTTP 401): invalid credentials.")
                    raise ElevenLabsAuthenticationException(
                        "ElevenLabs API authentication failed. Verify ELEVENLABS_API_KEY."
                    )

                if response.status_code == 404:
                    logger.warning(f"ElevenLabs voice_id '{voice_id}' not found (HTTP 404).")
                    raise ElevenLabsVoiceNotFoundException(voice_id=voice_id)

                if response.status_code == 429:
                    retry_after_str = response.headers.get("retry-after")
                    retry_after = int(retry_after_str) if retry_after_str and retry_after_str.isdigit() else 60
                    logger.warning(f"ElevenLabs rate limit or quota exceeded (HTTP 429), retry_after={retry_after}s.")
                    raise ElevenLabsRateLimitException(retry_after_seconds=retry_after)

                if response.status_code in (400, 422):
                    logger.error(f"ElevenLabs rejected payload with HTTP {response.status_code}: {response.text[:200]}")
                    raise ElevenLabsValidationException(
                        f"ElevenLabs validation error: {response.text[:150]}"
                    )

                # Handle Transient Server Errors (5xx)
                if response.status_code in (500, 502, 503, 504):
                    logger.warning(
                        f"ElevenLabs transient server error HTTP {response.status_code} on attempt {attempt}/{attempts}"
                    )
                    last_error = ElevenLabsUnavailableException(
                        f"ElevenLabs service returned HTTP {response.status_code}."
                    )

                else:
                    logger.error(f"Unexpected ElevenLabs status code HTTP {response.status_code}: {response.text[:200]}")
                    raise ElevenLabsException(
                        message=f"ElevenLabs unexpected error (HTTP {response.status_code}).",
                        status_code=response.status_code,
                    )

            except httpx.TimeoutException as exc:
                logger.warning(
                    f"ElevenLabs request timeout ({self.read_timeout}s) on attempt {attempt}/{attempts}: {exc}"
                )
                last_error = ElevenLabsTimeoutException(
                    timeout_seconds=self.read_timeout,
                    details={"attempt": attempt, "max_retries": self.max_retries},
                )
            except httpx.RequestError as exc:
                logger.warning(
                    f"ElevenLabs network connection error on attempt {attempt}/{attempts}: {exc}"
                )
                last_error = ElevenLabsUnavailableException(
                    f"Network error communicating with ElevenLabs: {type(exc).__name__}"
                )

            # If retries remain and error is transient, wait with exponential backoff
            if attempt < attempts:
                backoff = 0.25 * (2 ** (attempt - 1))
                logger.info(f"Retrying ElevenLabs call in {backoff:.2f}s (attempt {attempt + 1}/{attempts})...")
                await asyncio.sleep(backoff)

        # All attempts exhausted
        if last_error:
            raise last_error

        raise ElevenLabsUnavailableException("ElevenLabs call failed after maximum retries.")

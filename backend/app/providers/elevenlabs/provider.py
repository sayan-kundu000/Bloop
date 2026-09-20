"""
ElevenLabs TTS Provider Adapter
Implements the TTSProvider contract, orchestrating payload mapping, client execution,
and result normalization into TTSProviderResult.
"""

from typing import Any, Dict, Optional, Union
from backend.app.providers.base import TTSProvider, TTSProviderResult
from backend.app.providers.elevenlabs.client import ElevenLabsClient
from backend.app.providers.elevenlabs.mapper import ElevenLabsSettingsMapper


class ElevenLabsProvider(TTSProvider):
    """
    ElevenLabs Text-to-Speech Provider Adapter.
    Communicates securely via backend-to-backend REST calls without exposing credentials.
    """

    def __init__(
        self,
        client: Optional[ElevenLabsClient] = None,
        mapper: Optional[ElevenLabsSettingsMapper] = None,
    ):
        self.client = client or ElevenLabsClient()
        self.mapper = mapper or ElevenLabsSettingsMapper()

    def get_provider_name(self) -> str:
        """Returns the canonical provider identifier."""
        return "elevenlabs"

    def is_configured(self) -> bool:
        """Evaluates whether the ElevenLabs provider is configured with credentials."""
        return self.client.is_configured()

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        language_code: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        **kwargs,
    ) -> TTSProviderResult:
        """
        Synthesizes natural speech from text using ElevenLabs REST API.
        Returns a normalized TTSProviderResult.
        """
        # Combine settings and legacy options seamlessly
        combined_settings: Dict[str, Any] = {}
        if settings:
            combined_settings.update(settings)
        if options:
            combined_settings.update(options)

        # 1. Build and sanitize payload via allowlist mapper
        payload = self.mapper.build_payload(
            text=text,
            settings_dict=combined_settings,
            language_code=language_code,
        )

        output_format = self.mapper.resolve_output_format(combined_settings)

        # 2. Invoke ElevenLabs client
        audio_bytes, meta = await self.client.synthesize(
            voice_id=voice_id,
            payload=payload,
            output_format=output_format,
            request_id=request_id or kwargs.get("request_id"),
        )

        # 3. Construct normalized TTSProviderResult
        content_type = meta.get("content_type", "audio/mpeg")
        file_extension = "mp3" if "mpeg" in content_type or "mp3" in output_format else "wav"

        return TTSProviderResult(
            audio_bytes=audio_bytes,
            content_type=content_type,
            file_extension=file_extension,
            provider="elevenlabs",
            provider_request_id=meta.get("provider_request_id"),
            latency_ms=meta.get("latency_ms"),
            metadata=meta,
        )

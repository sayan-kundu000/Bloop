"""
Unit Tests for ElevenLabs Provider Adapter & Settings Mapper
Verifies contract adherence, settings sanitization, language code translation,
and generation of normalized TTSProviderResult.
"""

from unittest.mock import AsyncMock, MagicMock
import pytest

from backend.app.providers.base import TTSProvider, TTSProviderResult
from backend.app.providers.elevenlabs.client import ElevenLabsClient
from backend.app.providers.elevenlabs.mapper import ElevenLabsSettingsMapper
from backend.app.providers.elevenlabs.provider import ElevenLabsProvider
from backend.app.providers.elevenlabs.exceptions import ElevenLabsValidationException


class TestElevenLabsSettingsMapper:
    """Tests for payload sanitization and allowlist filtering."""

    def test_default_payload_construction(self):
        mapper = ElevenLabsSettingsMapper()
        payload = mapper.build_payload(
            text="Hello world",
            settings_dict=None,
            language_code="en-US",
        )
        assert payload["text"] == "Hello world"
        assert payload["model_id"] == "eleven_multilingual_v2"
        assert payload["language_code"] == "en"
        assert payload["voice_settings"]["stability"] == 0.5
        assert payload["voice_settings"]["similarity_boost"] == 0.75
        assert payload["voice_settings"]["style"] == 0.0
        assert payload["voice_settings"]["use_speaker_boost"] is True

    def test_clamps_out_of_range_voice_settings(self):
        mapper = ElevenLabsSettingsMapper()
        payload = mapper.build_payload(
            text="Testing range clamping",
            settings_dict={
                "stability": 2.5,  # Exceeds 1.0 -> must clamp to 1.0
                "similarity_boost": -0.5,  # Below 0.0 -> must clamp to 0.0
                "style": 99.0,  # Exceeds 1.0 -> clamp to 1.0
            },
        )
        assert payload["voice_settings"]["stability"] == 1.0
        assert payload["voice_settings"]["similarity_boost"] == 0.0
        assert payload["voice_settings"]["style"] == 1.0

    def test_language_code_mapping(self):
        mapper = ElevenLabsSettingsMapper()
        assert mapper.map_language_code("en-US") == "en"
        assert mapper.map_language_code("es-ES") == "es"
        assert mapper.map_language_code("fr_FR") == "fr"
        assert mapper.map_language_code("ja") == "ja"
        assert mapper.map_language_code(None) is None
        assert mapper.map_language_code("") is None

    def test_rejects_empty_text(self):
        mapper = ElevenLabsSettingsMapper()
        with pytest.raises(ElevenLabsValidationException):
            mapper.build_payload(text="   ")


class TestElevenLabsProvider:
    """Tests for ElevenLabsProvider adapter and TTSProvider contract conformance."""

    def test_provider_contract_conformance(self):
        provider = ElevenLabsProvider()
        assert isinstance(provider, TTSProvider)
        assert provider.get_provider_name() == "elevenlabs"

    @pytest.mark.asyncio
    async def test_provider_generates_tts_provider_result(self):
        mock_client = MagicMock(spec=ElevenLabsClient)
        mock_client.is_configured.return_value = True
        mock_client.synthesize = AsyncMock(
            return_value=(
                b"synthesized-audio-bytes",
                {
                    "provider_request_id": "el-test-req-123",
                    "content_type": "audio/mpeg",
                    "latency_ms": 142.5,
                },
            )
        )

        provider = ElevenLabsProvider(client=mock_client)
        assert provider.is_configured() is True

        result = await provider.generate_speech(
            text="Synthesizing test audio with ElevenLabs adapter.",
            voice_id="test-voice-id",
            language_code="en-US",
            settings={"stability": 0.7, "similarity_boost": 0.8},
            request_id="bloop-test-123",
        )

        assert isinstance(result, TTSProviderResult)
        assert result.audio_bytes == b"synthesized-audio-bytes"
        assert result.content_type == "audio/mpeg"
        assert result.file_extension == "mp3"
        assert result.provider == "elevenlabs"
        assert result.provider_request_id == "el-test-req-123"
        assert result.latency_ms == 142.5
        mock_client.synthesize.assert_called_once()

"""
ElevenLabs Settings Mapper
Validates, sanitizes, and translates Bloop request parameters and provider settings
into structured, vendor-compliant ElevenLabs API payloads.
Enforces strict allowlists to prevent untrusted JSON injection.
"""

from typing import Any, Dict, Optional
from backend.app.core.config import settings
from backend.app.providers.elevenlabs.exceptions import ElevenLabsValidationException


# Whitelisted ElevenLabs synthesis models
ALLOWED_MODELS = {
    "eleven_multilingual_v2",
    "eleven_turbo_v2",
    "eleven_turbo_v2_5",
    "eleven_monolingual_v1",
}

# Whitelisted ElevenLabs output audio formats
ALLOWED_OUTPUT_FORMATS = {
    "mp3_44100_128",
    "mp3_44100_64",
    "mp3_44100_192",
    "pcm_16000",
    "pcm_22050",
    "pcm_44100",
}


class ElevenLabsSettingsMapper:
    """Translates and validates settings into ElevenLabs REST API payloads."""

    def __init__(self, default_model_id: Optional[str] = None):
        self.default_model_id = (
            default_model_id
            or getattr(settings, "ELEVENLABS_DEFAULT_MODEL_ID", "eleven_multilingual_v2")
        )

    def map_language_code(self, language_code: Optional[str]) -> Optional[str]:
        """
        Converts Bloop language locales (e.g. 'en-US', 'es-ES') to ISO 639-1 ('en', 'es')
        as expected by ElevenLabs multilingual models.
        """
        if not language_code or not language_code.strip():
            return None
        clean = language_code.strip()
        # If locale contains a hyphen (e.g. en-US, pt-BR), take primary language subtag
        if "-" in clean:
            return clean.split("-")[0].lower()
        if "_" in clean:
            return clean.split("_")[0].lower()
        return clean.lower()

    def build_payload(
        self,
        text: str,
        settings_dict: Optional[Dict[str, Any]] = None,
        language_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Builds a strictly validated, sanitized JSON payload for ElevenLabs /text-to-speech/{voice_id}.
        Filters out arbitrary untrusted parameters and enforces range boundaries.
        """
        if not text or not text.strip():
            raise ElevenLabsValidationException("Text payload cannot be empty.")

        settings_dict = settings_dict or {}

        # 1. Resolve & validate model_id
        raw_model = settings_dict.get("model_id") or self.default_model_id
        if raw_model not in ALLOWED_MODELS:
            model_id = self.default_model_id
        else:
            model_id = raw_model

        # 2. Extract & clamp voice settings
        raw_voice_settings = settings_dict.get("voice_settings", {})
        if not isinstance(raw_voice_settings, dict):
            raw_voice_settings = {}

        # Merge top-level legacy shortcuts if provided
        stability_raw = raw_voice_settings.get("stability", settings_dict.get("stability", 0.5))
        similarity_raw = raw_voice_settings.get(
            "similarity_boost", settings_dict.get("similarity_boost", 0.75)
        )
        style_raw = raw_voice_settings.get("style", settings_dict.get("style", 0.0))
        speaker_boost_raw = raw_voice_settings.get(
            "use_speaker_boost", settings_dict.get("use_speaker_boost", True)
        )

        try:
            stability = max(0.0, min(1.0, float(stability_raw)))
        except (ValueError, TypeError):
            stability = 0.5

        try:
            similarity_boost = max(0.0, min(1.0, float(similarity_raw)))
        except (ValueError, TypeError):
            similarity_boost = 0.75

        try:
            style = max(0.0, min(1.0, float(style_raw)))
        except (ValueError, TypeError):
            style = 0.0

        use_speaker_boost = bool(speaker_boost_raw)

        payload: Dict[str, Any] = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost,
            },
        }

        # 3. Optional language code for multilingual models
        mapped_lang = self.map_language_code(language_code)
        if mapped_lang:
            payload["language_code"] = mapped_lang

        return payload

    def resolve_output_format(self, settings_dict: Optional[Dict[str, Any]] = None) -> str:
        """Resolves and validates the requested audio output format."""
        if not settings_dict:
            return "mp3_44100_128"

        fmt = settings_dict.get("output_format")
        if fmt and fmt in ALLOWED_OUTPUT_FORMATS:
            return fmt
        return "mp3_44100_128"

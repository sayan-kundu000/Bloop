"""
Bloop Speech Orchestration Service
Coordinates input validation, dynamic voice resolution, provider selection,
ElevenLabs audio synthesis, local caching, and database generation persistence.
"""

import os
import uuid
from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import TTSProvider, TTSProviderResult
from backend.app.providers.elevenlabs.exceptions import (
    ElevenLabsAuthenticationException,
    ElevenLabsException,
)
from backend.app.providers.elevenlabs.provider import ElevenLabsProvider
from backend.app.providers.mock_provider import MockTTSProvider
from backend.app.quantum.voice_modulator import QuantumVoiceModulator
from backend.app.repositories.generation_repository import GenerationRepository
from backend.app.schemas.tts import (
    QuantumResonanceMetrics,
    TextStatsResponse,
    TTSRequest,
    TTSResponse,
)
from backend.app.services.audio import (
    AudioDeliveryService,
    AudioProcessor,
    ProcessedAudio,
)
from backend.app.services.audio_dsp import AudioDSPService
from backend.app.services.capability_service import CapabilityService
from backend.app.core.exceptions import ErrorCode
from backend.app.services.speech.exceptions import (
    ProviderNotConfiguredException,
    SpeechPersistenceException,
)
from backend.app.services.speech.models import SpeechRequestDTO
from backend.app.services.text import TextProcessor, TextValidator
from backend.app.services.voice_service import VoiceService


class SpeechService:
    """
    Central Text-to-Speech Generation Engine.
    Orchestrates validation, external/internal provider dispatch,
    audio validation, temporary file caching, and generation metadata tracking.
    """

    def __init__(
        self,
        db: Session,
        elevenlabs_provider: Optional[TTSProvider] = None,
        mock_provider: Optional[TTSProvider] = None,
        audio_processor: Optional[AudioProcessor] = None,
        audio_delivery: Optional[AudioDeliveryService] = None,
    ):
        self.db = db
        self.gen_repo = GenerationRepository(db)
        self.voice_service = VoiceService(db)
        self.capability_service = CapabilityService(db)
        self.elevenlabs_provider = elevenlabs_provider or ElevenLabsProvider()
        self.mock_provider = mock_provider or MockTTSProvider()
        self.audio_processor = audio_processor or AudioProcessor()
        self.audio_delivery = audio_delivery or AudioDeliveryService()
        self.quantum_modulator = QuantumVoiceModulator()
        self.audio_dsp = AudioDSPService()
        self.text_processor = TextProcessor()
        self.text_validator = TextValidator()

    def analyze_text(self, text: str) -> TextStatsResponse:
        """
        Derives authoritative text metrics and evaluates length boundaries.
        """
        metrics = self.text_processor.analyze(text)
        min_chars = getattr(settings, "MIN_TEXT_CHARACTERS", 1)
        max_chars = getattr(settings, "MAX_TEXT_CHARACTERS", 2500)

        is_valid = True
        error_message = None

        if metrics.character_count < min_chars:
            is_valid = False
            error_message = "Text cannot be empty."
        elif metrics.character_count > max_chars:
            is_valid = False
            error_message = f"Text exceeds maximum limit of {max_chars} characters."

        return TextStatsResponse(
            char_count=metrics.character_count,
            word_count=metrics.word_count,
            estimated_duration_seconds=metrics.estimated_duration_seconds,
            is_valid=is_valid,
            error_message=error_message,
        )

    async def generate_speech(
        self,
        request: Union[TTSRequest, SpeechRequestDTO],
        user_id: Optional[int] = None,
        request_id: Optional[str] = None,
    ) -> TTSResponse:
        """
        Executes the complete TTS generation pipeline:
        1. Level 2 Backend Text Validation
        2. Level 3 Capability & Voice-Language Compatibility Validation
        3. Optional Quantum Acoustic Modulation
        4. Provider Resolution (ElevenLabs vs Simulation)
        5. Speech Synthesis Execution
        6. Temporary Audio Storage
        7. Metadata Persistence
        8. Standardized API Response
        """
        # 1. Authoritative Backend Text Validation (Level 2)
        metrics = self.text_validator.validate(request.text)
        normalized_text = metrics.normalized_text

        # 2. Authoritative Capability Validation (Level 3)
        requested_language = request.language or "en-US"
        voice, lang = self.capability_service.validate_tts_capability(
            voice_id=request.voice_id,
            language_code=requested_language,
        )
        voice_name = voice.name

        # 3. Optional Quantum Voice Modulation (Non-blocking fallback)
        quantum_res = None
        quantum_metrics = None
        try:
            quantum_res = self.quantum_modulator.modulate_voice(
                voice_id=request.voice_id,
                prompt_text=normalized_text,
                user_speed=request.speed or 1.0,
                user_pitch=request.pitch or 1.0,
                emotion=request.emotion or "Neutral",
            )
            av_ref = (
                quantum_res.audio_video_reference
                if (quantum_res.audio_video_reference and quantum_res.audio_video_reference.get("media_title"))
                else None
            )
            q_dec = (
                quantum_res.quantum_decision
                if (quantum_res.quantum_decision and quantum_res.quantum_decision.get("decided_delivery_mode"))
                else None
            )
            quantum_metrics = QuantumResonanceMetrics(
                quantum_fidelity=quantum_res.quantum_fidelity,
                quantum_emotion=quantum_res.quantum_emotion,
                entanglement_entropy=quantum_res.entanglement_entropy,
                resonance_verdict=quantum_res.resonance_verdict,
                canonical_source=quantum_res.canonical_source,
                applied_dsp_filter=quantum_res.dsp_profile.get("filter_type", "natural_warmth"),
                effective_pitch=quantum_res.effective_pitch_str,
                effective_rate=quantum_res.effective_rate_str,
                audio_video_reference=av_ref,
                quantum_decision=q_dec,
            )
            logger.info(
                f"Quantum modulation applied for '{request.voice_id}': fidelity={quantum_res.quantum_fidelity}, "
                f"emotion={quantum_res.quantum_emotion}"
            )
        except Exception as q_err:
            logger.warning(f"Quantum-RAG voice modulation skipped ({q_err})")

        # 4. Provider Resolution & Execution
        is_elevenlabs_voice = bool(voice and voice.provider == "elevenlabs")
        is_configured = self.elevenlabs_provider.is_configured()

        # Strict configuration check in production
        if is_elevenlabs_voice and not is_configured:
            if settings.APP_ENV == "production":
                raise ProviderNotConfiguredException(
                    provider="elevenlabs",
                    message="ElevenLabs API Key is not configured in production environment.",
                )
            logger.warning(
                "ElevenLabs API Key unconfigured in development/test. Falling back to simulation provider."
            )
            use_elevenlabs = False
        else:
            use_elevenlabs = is_elevenlabs_voice and is_configured

        audio_bytes: bytes
        audio_ext: str = "mp3"
        provider_name: str
        provider_request_id: Optional[str] = None
        is_simulation: bool = not use_elevenlabs

        custom_settings = getattr(request, "settings", None) or {}
        provider_result: Union[bytes, TTSProviderResult]
        provider_request_id: Optional[str] = None
        effective_user_id = user_id if user_id is not None else getattr(request, "user_id", None)

        try:
            if use_elevenlabs:
                provider_name = "elevenlabs"
                provider_result = await self.elevenlabs_provider.generate_speech(
                    text=normalized_text,
                    voice_id=request.voice_id,
                    language_code=requested_language,
                    settings=custom_settings,
                    options={"speed": request.speed, "pitch": request.pitch},
                    request_id=request_id or getattr(request, "request_id", None),
                )
                if isinstance(provider_result, TTSProviderResult):
                    provider_request_id = provider_result.provider_request_id
            else:
                provider_name = "simulation"
                provider_options = {
                    "language": requested_language,
                    "speed": request.speed,
                    "pitch": request.pitch,
                    "emotion": request.emotion,
                }
                if quantum_res:
                    provider_options["pitch_override"] = quantum_res.effective_pitch_str
                    provider_options["rate_override"] = quantum_res.effective_rate_str

                sim_result = await self.mock_provider.generate_speech(
                    text=normalized_text,
                    voice_id=request.voice_id,
                    options=provider_options,
                )
                if isinstance(sim_result, TTSProviderResult):
                    audio_bytes = sim_result.audio_bytes
                    audio_ext = sim_result.file_extension
                    provider_request_id = sim_result.provider_request_id
                else:
                    audio_bytes = bytes(sim_result)
                    audio_ext = "wav" if audio_bytes.startswith(b"RIFF") else "mp3"

                # Apply character-specific Audio DSP Filter
                if quantum_res and quantum_res.dsp_profile:
                    audio_bytes, audio_ext = self.audio_dsp.apply_character_dsp(
                        audio_bytes=audio_bytes,
                        dsp_profile=quantum_res.dsp_profile,
                    )
                provider_result = audio_bytes

            # 5. Audio Processing Layer: Validation, magic bytes, metadata extraction (Prompt 13 §10, §11)
            duration = metrics.estimated_duration_seconds
            processed_audio = self.audio_processor.process(
                provider_result=provider_result,
                fallback_duration=duration,
            )
        except Exception as synth_err:
            logger.error(
                f"Speech synthesis or audio validation failed: provider={provider_name}, "
                f"chars={metrics.character_count}, error={synth_err}"
            )
            try:
                err_code = getattr(synth_err, "code", ErrorCode.AUDIO_GENERATION_FAILED)
                self.gen_repo.record_failure(
                    text=normalized_text,
                    char_count=metrics.character_count,
                    word_count=metrics.word_count,
                    language_code=requested_language,
                    voice_id=request.voice_id,
                    provider=provider_name,
                    error_code=str(err_code),
                    error_message=str(synth_err),
                    user_id=effective_user_id,
                    voice_name=voice_name,
                )
            except Exception as audit_err:
                logger.warning(f"Could not record failed generation record: {audit_err}")
                self.db.rollback()
            raise synth_err

        # 6. Audio Delivery Layer: Safe temporary storage (Prompt 13 §15, §19)
        audio_filename = self.audio_delivery.store_temporary_audio(
            audio_bytes=processed_audio.audio_bytes,
            extension=processed_audio.metadata.file_extension,
        )

        file_size = processed_audio.metadata.file_size_bytes
        audio_ext = processed_audio.metadata.file_extension
        content_type = processed_audio.metadata.content_type
        effective_duration = processed_audio.metadata.duration_seconds or duration

        # 7. Record generation metadata in database with transaction safety
        try:
            gen_record = self.gen_repo.create(
                user_id=effective_user_id,
                text=normalized_text,
                char_count=metrics.character_count,
                word_count=metrics.word_count,
                language_code=requested_language,
                voice_id=request.voice_id,
                voice_name=voice_name,
                audio_filename=audio_filename,
                duration_seconds=effective_duration,
                file_size_bytes=file_size,
                provider=provider_name,
                provider_request_id=provider_request_id,
                status="completed",
                audio_format=audio_ext,
            )
            generation_id = gen_record.id
        except Exception as db_err:
            logger.error(f"Failed to persist generation metadata: {db_err}", exc_info=True)
            self.db.rollback()
            # Prune orphaned temporary audio file from disk
            self.audio_delivery.delete_audio_file(audio_filename)
            raise SpeechPersistenceException(f"Database error during generation persistence: {db_err}")

        logger.info(
            f"Speech generated successfully: generation_id={generation_id}, provider={provider_name}, "
            f"chars={metrics.character_count}, words={metrics.word_count}"
        )

        audio_url = f"{settings.API_V1_STR}/tts/audio/{audio_filename}"
        download_url = f"{settings.API_V1_STR}/tts/download/{audio_filename}"

        return TTSResponse(
            generation_id=generation_id,
            audio_url=audio_url,
            download_url=download_url,
            text=normalized_text,
            char_count=metrics.character_count,
            word_count=metrics.word_count,
            language=requested_language,
            voice_id=request.voice_id,
            voice_name=voice_name,
            duration_seconds=effective_duration,
            provider=provider_name,
            is_simulation=is_simulation,
            emotion=request.emotion,
            content_type=content_type,
            audio_format=audio_ext,
            quantum_metrics=quantum_metrics,
        )

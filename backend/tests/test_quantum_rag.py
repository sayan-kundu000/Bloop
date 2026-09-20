import pytest
import numpy as np
import wave
import io
from backend.app.quantum.voice_rag import VoiceRAGService
from backend.app.quantum.voice_modulator import QuantumVoiceModulator
from backend.app.services.audio_dsp import AudioDSPService
from backend.app.services.tts_service import TTSService
from backend.app.schemas.tts import TTSRequest


def test_voice_rag_retrieval():
    rag = VoiceRAGService()

    # Normal Female US profile lookup
    en_female = rag.retrieve_augmented_context("normal-female", "Welcome to Bloop AI speech synthesis")
    assert "North American Female" in en_female["canonical_source"]
    assert en_female["acoustic_dsp"]["filter_type"] == "natural_warmth"
    assert en_female["audio_video_reference"] is not None
    assert "Broadcast Studio Reference" in en_female["audio_video_reference"]["media_title"]

    # Normal Male US profile lookup
    en_male = rag.retrieve_augmented_context("normal-male", "High fidelity audio processing")
    assert "North American Male" in en_male["canonical_source"]
    assert en_male["acoustic_dsp"]["filter_type"] == "natural_warmth"

    # Fallback for unregistered voice
    unregistered = rag.retrieve_augmented_context("custom-voice-xyz", "Hello there")
    assert unregistered["canonical_source"] == "Standard Acoustic Model"


def test_100_percent_voice_catalog_coverage():
    from backend.app.db.init_db import DYNAMIC_VOICE_TEMPLATES
    from backend.app.quantum.voice_rag import VOICE_RAG_CORPUS

    all_voice_ids = [v["voice_id"] for v in DYNAMIC_VOICE_TEMPLATES]
    assert len(all_voice_ids) == 2
    assert "normal-male" in all_voice_ids
    assert "normal-female" in all_voice_ids

    missing = []
    for vid in all_voice_ids:
        if vid not in VOICE_RAG_CORPUS:
            missing.append(vid)
            continue
        entry = VOICE_RAG_CORPUS[vid]
        assert len(entry["character_name"]) > 0
        assert len(entry["canonical_source"]) > 0
        assert len(entry["lore_text"]) > 0
        assert "filter_type" in entry["acoustic_dsp"]

    assert len(missing) == 0, f"Missing RAG voice profiles: {missing}"


def test_quantum_voice_modulator():
    modulator = QuantumVoiceModulator()
    res = modulator.modulate_voice(
        voice_id="normal-female",
        prompt_text="Welcome to Bloop dynamic AI text to speech studio.",
        user_speed=1.0,
        user_pitch=1.0,
    )

    assert res.voice_id == "normal-female"
    assert "North American Female" in res.canonical_source
    assert res.quantum_fidelity >= 0.0
    assert res.dsp_profile["filter_type"] == "natural_warmth"
    assert res.effective_pitch_str.endswith("Hz")

    # Verify Audio/Video Reference Benchmark & Quantum Decision
    assert res.audio_video_reference is not None
    assert "Broadcast Studio Reference" in res.audio_video_reference["media_title"]
    assert res.audio_video_reference["acoustic_benchmark"]["f0_median_hz"] > 100.0

    assert res.quantum_decision is not None
    assert len(res.quantum_decision["pauli_z_expectations"]) == 4
    for z in res.quantum_decision["pauli_z_expectations"]:
        assert -1.0 <= z <= 1.0
    assert res.quantum_decision["decided_delivery_mode"] is not None
    assert len(res.quantum_decision["decision_rationale"]) > 5


def test_audio_dsp_processing():
    dsp = AudioDSPService()
    sample_rate = 24000
    t = np.linspace(0, 0.5, int(sample_rate * 0.5))
    tone = (np.sin(2 * np.pi * 200 * t) * 20000).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(tone.tobytes())
    wav_bytes = buf.getvalue()

    profile = {
        "filter_type": "natural_warmth",
        "bass_boost_db": 2.0,
        "wet_mix": 0.3,
    }
    processed, ext = dsp.apply_character_dsp(wav_bytes, profile)
    assert ext == "wav"
    assert len(processed) > 100


@pytest.mark.asyncio
async def test_tts_service_with_quantum_rag(db_session):
    tts = TTSService(db_session)
    req = TTSRequest(
        text="Experience high-fidelity speech synthesis with Bloop.",
        language="en-US",
        voice_id="normal-female",
        speed=1.0,
        pitch=1.0,
    )

    resp = await tts.generate_speech(req)
    assert resp.generation_id is not None
    assert resp.audio_url.startswith("/api/v1/tts/audio/")
    assert resp.quantum_metrics is not None
    assert resp.quantum_metrics.quantum_fidelity >= 0.0
    assert "North American Female" in resp.quantum_metrics.canonical_source
    assert resp.quantum_metrics.applied_dsp_filter == "natural_warmth"

    # Verify Audio/Video Reference & Quantum Decision details in API Response
    assert resp.quantum_metrics.audio_video_reference is not None
    assert "Broadcast Studio Reference" in resp.quantum_metrics.audio_video_reference.media_title
    assert resp.quantum_metrics.audio_video_reference.clip_timestamp is not None
    assert resp.quantum_metrics.quantum_decision is not None
    assert len(resp.quantum_metrics.quantum_decision.pauli_z_expectations) == 4
    assert resp.quantum_metrics.quantum_decision.decided_delivery_mode is not None

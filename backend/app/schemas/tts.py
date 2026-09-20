"""
Bloop Text-to-Speech (TTS) Schemas
Defines request contracts, resonance metrics, audio metadata, and text analysis payloads.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


class TTSRequest(BaseModel):
    """Core request payload for synthesizing natural speech from text."""
    text: str = Field(..., max_length=10000, description="Text content to be synthesized into natural speech")
    language: str = Field("en-US", description="Language code matching selected voice (e.g. en-US)")
    voice_id: str = Field(..., description="Selected dynamic voice identifier")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech rate multiplier (0.5 to 2.0)")
    pitch: Optional[float] = Field(1.0, ge=0.5, le=1.5, description="Speech pitch multiplier (0.5 to 1.5)")
    emotion: Optional[str] = Field("Neutral", description="Selected emotional delivery tone")
    settings: Optional[Dict[str, Any]] = Field(None, description="Optional vendor-specific settings (e.g. stability, similarity_boost)")


class TextAnalyzeRequest(BaseModel):
    """Payload for real-time text analysis before synthesis."""
    text: str = Field(..., max_length=10000, description="Raw text string to analyze for stats and limits")


class AudioVideoReference(BaseModel):
    """Canonical ground-truth reference for acoustic and cinematic verification."""
    media_title: str = Field(..., description="Canonical media title (film, show, speech, interview)")
    scene_timestamp: Optional[str] = Field(None, description="Exact scene timestamp or episode identifier")
    clip_timestamp: Optional[str] = Field(None, description="Exact scene timestamp or episode identifier")
    scene_context: str = Field(..., description="Contextual and physical acoustic scene description")
    acoustic_benchmark: Dict[str, Any] = Field(default_factory=dict, description="Ground-truth acoustic parameters (F0, formants, tempo)")


class QuantumDecisionDetails(BaseModel):
    """Explains how quantum expectation values shaped acoustic modulation."""
    pauli_z_expectations: List[float] = Field(..., description="Pauli-Z expectation values [<Z0>, <Z1>, <Z2>, <Z3>]")
    decided_pitch_hz: int = Field(..., description="Continuous pitch shift decided by quantum expectation <Z0>")
    decided_rate_pct: int = Field(..., description="Speech tempo percentage decided by quantum expectation <Z1>")
    decided_dsp_filter: str = Field(..., description="Acoustic filter decided by quantum statevector overlap")
    decided_delivery_mode: str = Field(..., description="Vocal delivery mode resolved by quantum projective basis")
    decision_rationale: str = Field(..., description="Human-readable explanation of quantum decision computation")


class QuantumResonanceMetrics(BaseModel):
    """Resonance and quantum fidelity metrics returned from optional quantum modulation."""
    quantum_fidelity: float = Field(..., description="Hilbert-space quantum transition fidelity [0, 1]")
    quantum_emotion: str = Field(..., description="Detected affective state from PennyLane QNN")
    entanglement_entropy: float = Field(..., description="Shannon quantum entanglement entropy")
    resonance_verdict: str = Field(..., description="Canonical lore resonance classification")
    canonical_source: str = Field(..., description="Primary reference source for the character voice")
    applied_dsp_filter: str = Field(..., description="Active acoustic DSP filter applied to speech")
    effective_pitch: Optional[str] = None
    effective_rate: Optional[str] = None
    audio_video_reference: Optional[AudioVideoReference] = None
    quantum_decision: Optional[QuantumDecisionDetails] = None


class TTSResponse(BaseModel):
    """Response payload returned upon speech synthesis generation."""
    generation_id: Optional[int] = Field(None, description="ID of the persisted SpeechGeneration record")
    audio_url: str = Field(..., description="Relative or absolute URL to stream generated audio")
    download_url: str = Field(..., description="Direct download URL for audio file with attachment header")
    text: str = Field(..., description="Synthesized text")
    char_count: int = Field(..., description="Character count")
    word_count: int = Field(..., description="Word count")
    language: str = Field(..., description="Language locale")
    voice_id: str = Field(..., description="Voice identifier used")
    voice_name: Optional[str] = Field(None, description="Voice display name")
    duration_seconds: Optional[float] = Field(0.0, description="Audio duration in seconds")
    provider: str = Field("elevenlabs", description="Synthesis provider")
    is_simulation: bool = Field(False, description="Whether output was generated via local simulation")
    emotion: Optional[str] = Field(None, description="Selected emotion tone")
    content_type: str = Field("audio/mpeg", description="MIME content type of generated audio")
    audio_format: str = Field("mp3", description="Audio format container (mp3 or wav)")
    quantum_metrics: Optional[QuantumResonanceMetrics] = Field(None, description="Quantum modulation metrics if enabled")


class TextStatsResponse(BaseModel):
    """Real-time text analysis statistics."""
    char_count: int = Field(..., description="Total character count")
    word_count: int = Field(..., description="Total word count")
    estimated_duration_seconds: float = Field(..., description="Estimated speech duration in seconds")
    is_valid: bool = Field(..., description="Whether text meets validation length constraints")
    error_message: Optional[str] = Field(None, description="Validation failure explanation if invalid")

"""
Quantum Emotion Intelligence — Pydantic Schemas
Defines request validation and serialized API response contracts.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class SpeechRecommendationPayload(BaseModel):
    """Suggested speech synthesis delivery parameters."""
    style: str
    speed: float = Field(1.0, ge=0.5, le=2.0)
    pitch: float = Field(1.0, ge=0.5, le=1.5)
    stability: float = Field(0.5, ge=0.0, le=1.0)
    similarity_boost: float = Field(0.75, ge=0.0, le=1.0)
    pacing: str
    reason: str
    confidence: Optional[float] = None
    applied: bool = False


class EmotionExperimentRequest(BaseModel):
    """Payload for analyzing text emotion using the Hybrid QNN."""
    text: str = Field(..., min_length=1, max_length=1000, description="Natural language input text (<= 1000 chars)")
    shots: int = Field(1024, ge=100, le=4096, description="Quantum measurement shots")
    num_qubits: int = Field(4, ge=2, le=8, description="Allocated quantum register width")
    circuit_depth: int = Field(4, ge=1, le=8, description="Maximum circuit depth")
    framework: Optional[str] = Field("pennylane", description="Target framework: 'pennylane' or 'qiskit'")
    include_recommendation: bool = Field(True, description="Whether to include optional speech synthesis recommendation")


class EmotionExperimentResponse(BaseModel):
    """Normalized response from the Quantum Emotion Intelligence pipeline."""
    input_text: str
    detected_emotion: str
    emotion_scores: Dict[str, float]
    quantum_probabilities: Dict[str, float]
    hybrid_qnn_confidence: Optional[float] = None
    classical_baseline_emotion: str
    classical_confidence: Optional[float] = None
    entanglement_entropy: float
    circuit_depth: int
    num_qubits: int
    execution_time_ms: float

    # Prompt 24 Enrichments
    speech_recommendation: Optional[SpeechRecommendationPayload] = None
    metrics: Optional[Dict[str, Any]] = None
    classical_baseline: Optional[Dict[str, Any]] = None
    quantum: Optional[Dict[str, Any]] = None
    pipeline_steps: Optional[List[str]] = None

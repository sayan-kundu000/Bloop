"""
Quantum Emotion Intelligence — Domain Models & Dataclasses
Defines internal entities, metrics, and data transfer containers.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from backend.app.quantum.emotion.labels import EmotionLabel


class QNNFramework(str, Enum):
    """Quantum execution frameworks supported for the Hybrid QNN."""
    PENNYLANE = "pennylane"
    QISKIT = "qiskit"


class RecommendationPacing(str, Enum):
    """Vocal delivery pacing categories."""
    SLOW = "slow"
    MODERATE = "moderate"
    DYNAMIC = "dynamic"
    FAST = "fast"


@dataclass
class SpeechRecommendation:
    """
    Suggested Acoustic Synthesis Parameters.
    Strictly decoupled: recommendation never overrides user settings automatically
    and never calls ElevenLabs directly.
    """
    style: str
    speed: float
    pitch: float
    stability: float
    similarity_boost: float
    pacing: str
    reason: str
    confidence: Optional[float] = None
    applied: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "style": self.style,
            "speed": self.speed,
            "pitch": self.pitch,
            "stability": self.stability,
            "similarity_boost": self.similarity_boost,
            "pacing": self.pacing,
            "reason": self.reason,
            "confidence": self.confidence,
            "applied": self.applied,
        }


@dataclass
class EmotionMetrics:
    """Standardized empirical classification metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_time_seconds: float
    inference_time_seconds: float
    quantum_execution_time_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "training_time_seconds": round(self.training_time_seconds, 4),
            "inference_time_seconds": round(self.inference_time_seconds, 4),
            "quantum_execution_time_seconds": round(self.quantum_execution_time_seconds, 4),
        }


@dataclass
class EmotionClassificationResult:
    """Aggregated result from hybrid quantum classification and classical baseline."""
    input_text: str
    detected_emotion: str
    emotion_scores: Dict[str, float]
    quantum_probabilities: Dict[str, float]
    hybrid_qnn_confidence: Optional[float]
    classical_baseline_emotion: str
    classical_confidence: Optional[float]
    entanglement_entropy: float
    circuit_depth: int
    num_qubits: int
    execution_time_ms: float
    framework: str = "pennylane"
    speech_recommendation: Optional[SpeechRecommendation] = None
    metrics: Optional[EmotionMetrics] = None
    classical_baseline_details: Optional[Dict[str, Any]] = None
    pipeline_steps: List[str] = field(default_factory=list)

"""
Quantum Emotion Analyzer — Legacy Compatibility Adapter
Delegates to the modular QuantumEmotionService while maintaining backward compatibility.
"""

from backend.app.schemas.quantum import QuantumEmotionResponse
from backend.app.quantum.emotion import QuantumEmotionService, EmotionExperimentRequest


class QuantumEmotionAnalyzer:
    """
    Backward-compatible facade for Quantum Emotion Intelligence.
    Delegates to QuantumEmotionService.
    """

    def __init__(self, shots: int = 1024):
        self.shots = shots
        self.num_qubits = 4
        self.service = QuantumEmotionService()

    def analyze(self, text: str) -> QuantumEmotionResponse:
        req = EmotionExperimentRequest(
            text=text,
            shots=self.shots,
            num_qubits=self.num_qubits,
            framework="pennylane",
            include_recommendation=True,
        )
        res = self.service.analyze_emotion(req)
        return QuantumEmotionResponse(
            input_text=res.input_text,
            detected_emotion=res.detected_emotion,
            emotion_scores=res.emotion_scores,
            quantum_probabilities=res.quantum_probabilities,
            hybrid_qnn_confidence=res.hybrid_qnn_confidence if res.hybrid_qnn_confidence is not None else 0.85,
            classical_baseline_emotion=res.classical_baseline_emotion,
            classical_confidence=res.classical_confidence if res.classical_confidence is not None else 0.85,
            entanglement_entropy=res.entanglement_entropy,
            circuit_depth=res.circuit_depth,
            num_qubits=res.num_qubits,
            execution_time_ms=res.execution_time_ms,
            speech_recommendation=res.speech_recommendation.model_dump() if res.speech_recommendation else None,
            metrics=res.metrics,
            classical_baseline=res.classical_baseline,
            quantum=res.quantum,
            pipeline_steps=res.pipeline_steps,
        )

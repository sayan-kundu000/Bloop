"""
Bloop Quantum Intelligence Candidate Adapters
Wraps existing quantum services (Prompts 23-26) to provide normalized
candidate interfaces for hybrid intelligence and benchmarking.
"""

import time
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.quantum.config import quantum_config
from backend.app.quantum.exceptions import HybridExecutionFailedException


class QuantumCandidateAdapter:
    """Provides normalized execution interfaces across quantum intelligence domains."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    def evaluate_text(
        self,
        text: str,
        num_qubits: int = 4,
        shots: int = 1024,
    ) -> Tuple[str, Dict[str, float], float]:
        """Executes Quantum Text Intelligence variational classification."""
        from backend.app.quantum.text import QuantumTextService, QuantumTextExperimentRequest

        t0 = time.perf_counter()
        service = QuantumTextService(db=self.db)
        req = QuantumTextExperimentRequest(
            text=text,
            task="classification",
            model="hybrid_quantum_classifier",
            framework="qiskit",
            num_qubits=num_qubits,
            shots=shots,
            circuit_depth=quantum_config.text_circuit_depth,
        )
        res = service.analyze_text(req)
        latency = time.perf_counter() - t0

        predicted_style = res.predicted_style
        probs = res.quantum_probabilities or {}
        return predicted_style, probs, latency

    def evaluate_emotion(
        self,
        text: str,
        num_qubits: int = 4,
        shots: int = 1024,
    ) -> Tuple[str, Dict[str, float], float]:
        """Executes Quantum Emotion Intelligence PennyLane QNN analysis."""
        from backend.app.quantum.emotion import QuantumEmotionService, EmotionExperimentRequest

        t0 = time.perf_counter()
        service = QuantumEmotionService(db=self.db)
        req = EmotionExperimentRequest(
            text=text,
            shots=shots,
            num_qubits=num_qubits,
            circuit_depth=quantum_config.emotion_circuit_depth,
            framework="pennylane",
            include_recommendation=False,
        )
        res = service.analyze_emotion(req)
        latency = time.perf_counter() - t0

        detected_emotion = res.detected_emotion
        scores = res.emotion_scores or {}
        return detected_emotion, scores, latency

    def evaluate_semantics(
        self,
        text_a: str,
        text_b: str,
        num_qubits: int = 4,
        shots: int = 1024,
    ) -> Tuple[float, float]:
        """Executes Quantum Semantic Intelligence kernel state fidelity."""
        from backend.app.quantum.semantic import QuantumSemanticService, SemanticAnalysisRequest

        t0 = time.perf_counter()
        service = QuantumSemanticService(db=self.db)
        req = SemanticAnalysisRequest(
            text_a=text_a,
            text_b=text_b,
            method="quantum",
            framework="qiskit",
            num_qubits=num_qubits,
            shots=shots,
        )
        res = service.analyze_similarity(req)
        latency = time.perf_counter() - t0

        return round(float(res.quantum_kernel_similarity), 4), latency

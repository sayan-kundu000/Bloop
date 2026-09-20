from typing import Optional
from backend.app.quantum.text import QuantumTextService, QuantumTextExperimentRequest
from backend.app.schemas.quantum import QuantumTextResponse

STYLES = ["formal", "casual", "technical", "creative"]


class QuantumTextClassifier:
    """
    Quantum Text Intelligence Module.
    Encodes text features into quantum states and executes a Variational Quantum Classifier (VQC)
    alongside a classical baseline classifier.
    Delegates to the modular QuantumTextService pipeline.
    """

    def __init__(self, num_qubits: int = 4, shots: int = 1024):
        self.num_qubits = min(max(num_qubits, 2), 8)
        self.shots = shots
        self.service = QuantumTextService()

    def classify(self, text: str) -> QuantumTextResponse:
        req = QuantumTextExperimentRequest(
            text=text,
            num_qubits=self.num_qubits,
            shots=self.shots,
        )
        res = self.service.analyze_text(req)
        return QuantumTextResponse(
            input_text=res.input_text,
            tokens=res.tokens,
            classical_features=res.classical_features,
            quantum_probabilities=res.quantum_probabilities,
            predicted_style=res.predicted_style,
            confidence=res.confidence if res.confidence is not None else 0.85,
            classical_baseline_prediction=res.classical_baseline_prediction,
            classical_confidence=res.classical_confidence if res.classical_confidence is not None else 0.85,
            circuit_depth=res.circuit_depth,
            num_qubits=res.num_qubits,
            execution_time_ms=res.execution_time_ms,
            task=res.task,
            model=res.model,
            prediction=res.prediction,
            metrics=res.metrics.model_dump() if res.metrics else None,
            quantum=res.quantum.model_dump() if res.quantum else None,
            pipeline_steps=res.pipeline_steps,
            classical_baseline=res.classical_baseline,
        )


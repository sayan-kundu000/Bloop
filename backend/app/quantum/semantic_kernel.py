"""
Quantum Semantic Kernel Adapter (Prompt 22 & 25 Compatibility).
Provides backward-compatible interface delegating to the unified QuantumSemanticService.
"""

from typing import Optional
from backend.app.schemas.quantum import QuantumSemanticResponse
from backend.app.quantum.semantic import QuantumSemanticService, SemanticAnalysisRequest


class QuantumSemanticEstimator:
    """
    Quantum Semantic Intelligence Module.
    Estimates semantic text similarity using Quantum Kernel State Fidelity:
    K(x_A, x_B) = |<phi(x_A) | phi(x_B)>|^2
    measured via transition probability to the ground state |0...0>.
    Delegates to the research-grade QuantumSemanticService.
    """

    def __init__(self, num_qubits: int = 4):
        self.num_qubits = min(max(num_qubits, 2), 8)
        self.service = QuantumSemanticService()

    def compare(self, text_a: str, text_b: str) -> QuantumSemanticResponse:
        req = SemanticAnalysisRequest(
            text_a=text_a,
            text_b=text_b,
            method="hybrid",
            framework="qiskit",
            num_qubits=self.num_qubits,
            shots=1024,
        )
        res = self.service.analyze_similarity(req)
        return QuantumSemanticResponse(
            text_a=res.text_a,
            text_b=res.text_b,
            quantum_kernel_similarity=res.quantum_kernel_similarity,
            classical_cosine_similarity=res.classical_cosine_similarity,
            similarity_verdict=res.similarity_verdict,
            divergence=res.divergence,
            num_qubits=res.num_qubits,
            circuit_depth=res.circuit_depth,
            execution_time_ms=res.execution_time_ms,
            method=res.method,
            similarity_score=res.similarity_score,
            classical_similarity=res.classical_similarity,
            quantum_similarity=res.quantum_similarity,
            hybrid_similarity=res.hybrid_similarity,
            semantic_distance=res.semantic_distance,
            feature_dimension=res.feature_dimension,
            reduced_dimension=res.reduced_dimension,
            representation_method=res.representation_method,
            reduction_method=res.reduction_method,
            encoding_method=res.encoding_method,
            quantum_framework=res.quantum_framework,
            quantum_backend=res.quantum_backend,
            shots=res.shots,
            experiment_id=res.experiment_id,
            pipeline_steps=res.pipeline_steps,
        )

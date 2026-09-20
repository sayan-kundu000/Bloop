"""
Bloop Normalized Quantum Result
Strictly encapsulates quantum simulation outputs into a JSON-safe, framework-agnostic schema.
Derived probabilities are calculated deterministically: P(s) = count(s) / total_shots.
Raw framework objects (Qiskit Results, PennyLane Tensors, NumPy values) are never leaked.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from backend.app.quantum.domain.models import ExecutionStatus, QuantumFramework


class NormalizedQuantumResult(BaseModel):
    """Normalized, framework-independent quantum execution result."""

    experiment_id: Optional[str] = None
    framework: str = Field(default=QuantumFramework.QISKIT.value)
    backend: str = Field(default="aer_simulator")
    qubits: int = Field(..., ge=1)
    shots: int = Field(..., ge=1)
    counts: Dict[str, int] = Field(default_factory=dict)
    probabilities: Dict[str, float] = Field(default_factory=dict)
    circuit_depth: int = Field(default=0)
    total_gates: int = Field(default=0)
    qasm: Optional[str] = None
    circuit_diagram_ascii: Optional[str] = None
    is_noisy_simulation: bool = False
    execution_time_ms: float = Field(default=0.0)
    status: str = Field(default=ExecutionStatus.COMPLETED.value)
    metrics: Optional[Dict[str, Any]] = None

    @classmethod
    def from_counts(
        cls,
        counts: Dict[str, int],
        shots: int,
        qubits: int,
        framework: str = QuantumFramework.QISKIT.value,
        backend: str = "aer_simulator",
        execution_time_ms: float = 0.0,
        circuit_depth: int = 0,
        total_gates: int = 0,
        qasm: Optional[str] = None,
        circuit_diagram_ascii: Optional[str] = None,
        is_noisy_simulation: bool = False,
        status: str = ExecutionStatus.COMPLETED.value,
        metrics: Optional[Dict[str, Any]] = None,
        experiment_id: Optional[str] = None,
    ) -> "NormalizedQuantumResult":
        """Constructs a normalized result and derives state probabilities."""
        safe_shots = max(shots, 1)
        safe_counts = {str(k): int(v) for k, v in counts.items()}
        derived_probs = {
            k: round(v / safe_shots, 4) for k, v in safe_counts.items()
        }

        return cls(
            experiment_id=experiment_id,
            framework=framework,
            backend=backend,
            qubits=qubits,
            shots=safe_shots,
            counts=safe_counts,
            probabilities=derived_probs,
            circuit_depth=circuit_depth,
            total_gates=total_gates,
            qasm=qasm,
            circuit_diagram_ascii=circuit_diagram_ascii,
            is_noisy_simulation=is_noisy_simulation,
            execution_time_ms=round(float(execution_time_ms), 2),
            status=status,
            metrics=metrics,
        )

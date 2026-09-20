"""
Bloop Qiskit Converters
Safely converts Qiskit execution outputs into normalized, JSON-safe data structures.
"""

from typing import Any, Dict, Optional
from backend.app.quantum.domain.result import NormalizedQuantumResult
from backend.app.quantum.domain.models import QuantumFramework, ExecutionStatus


def qiskit_result_to_normalized(
    counts: Dict[str, int],
    shots: int,
    num_qubits: int,
    execution_time_ms: float,
    circuit_depth: int = 0,
    total_gates: int = 0,
    qasm: Optional[str] = None,
    circuit_diagram_ascii: Optional[str] = None,
    is_noisy: bool = False,
    experiment_id: Optional[str] = None,
) -> NormalizedQuantumResult:
    """
    Translates raw Qiskit measurement counts into NormalizedQuantumResult.
    Guarantees that all numbers are standard Python ints and floats.
    """
    safe_counts: Dict[str, int] = {}
    for state, cnt in counts.items():
        # Ensure standard Python types
        safe_counts[str(state)] = int(cnt)

    return NormalizedQuantumResult.from_counts(
        counts=safe_counts,
        shots=int(shots),
        qubits=int(num_qubits),
        framework=QuantumFramework.QISKIT.value,
        backend="aer_simulator",
        execution_time_ms=float(execution_time_ms),
        circuit_depth=int(circuit_depth),
        total_gates=int(total_gates),
        qasm=qasm,
        circuit_diagram_ascii=circuit_diagram_ascii,
        is_noisy_simulation=bool(is_noisy),
        status=ExecutionStatus.COMPLETED.value,
        experiment_id=experiment_id,
    )

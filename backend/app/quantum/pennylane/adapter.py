"""
Bloop PennyLane Adapter
Implements QuantumBackend using PennyLane and its high-performance simulation devices.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Sequence
import numpy as np

from backend.app.quantum.domain.models import QuantumFramework, ExecutionStatus
from backend.app.quantum.domain.result import NormalizedQuantumResult
from backend.app.quantum.execution.backend import QuantumBackend
from backend.app.quantum.execution.limits import validate_execution_parameters
from backend.app.quantum.exceptions import QuantumExecutionError


class PennyLaneAdapter(QuantumBackend):
    """Execution adapter for PennyLane differentiable quantum simulations."""

    @property
    def name(self) -> str:
        return "pennylane_default_qubit"

    @property
    def framework(self) -> str:
        return QuantumFramework.PENNYLANE.value

    def get_device(self, num_qubits: int, shots: int = 1024, use_qiskit_backend: bool = False):
        """Constructs a PennyLane simulation device."""
        import pennylane as qml

        if use_qiskit_backend:
            try:
                # Interoperability path: PennyLane running on Qiskit Aer
                return qml.device("qiskit.aer", wires=num_qubits, shots=shots)
            except Exception:
                pass

        return qml.device("default.qubit", wires=num_qubits, shots=shots)

    def execute(
        self,
        circuit: Any,
        shots: int = 1024,
        seed: Optional[int] = None,
        noise_level: float = 0.0,
        **kwargs: Any,
    ) -> NormalizedQuantumResult:
        """
        Executes a PennyLane circuit callable or basic template.
        Returns a normalized JSON-safe quantum result.
        """
        import pennylane as qml

        num_qubits = int(kwargs.get("num_qubits", 2))
        validate_execution_parameters(num_qubits, shots)

        start_time = time.perf_counter()
        use_qiskit = bool(
            kwargs.get("use_qiskit_backend", False)
            or kwargs.get("backend") in ("qiskit.aer", "qiskit_aer")
        )
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                dev = self.get_device(
                    num_qubits=num_qubits,
                    shots=shots,
                    use_qiskit_backend=use_qiskit,
                )

            # If a custom quantum function is provided
            if callable(circuit):
                @qml.qnode(dev)
                def qnode():
                    circuit(wires=range(num_qubits))
                    return qml.counts(all_outcomes=True)
            else:
                # Default baseline circuit: superposition on wire 0, entangle with wire 1 (if available)
                @qml.qnode(dev)
                def qnode():
                    qml.Hadamard(wires=0)
                    if num_qubits > 1:
                        qml.CNOT(wires=[0, 1])
                    return qml.counts(all_outcomes=True)

            raw_counts = qnode()
        except Exception as e:
            raise QuantumExecutionError(f"PennyLane execution failed: {e}")

        execution_time_ms = (time.perf_counter() - start_time) * 1000.0

        # Convert PennyLane counts dictionary to safe python primitives
        safe_counts: Dict[str, int] = {}
        for state, cnt in raw_counts.items():
            safe_counts[str(state)] = int(cnt)

        return NormalizedQuantumResult.from_counts(
            counts=safe_counts,
            shots=shots,
            qubits=num_qubits,
            framework=self.framework,
            backend=str(dev.name),
            execution_time_ms=execution_time_ms,
            circuit_depth=1 if num_qubits == 1 else 2,
            total_gates=num_qubits,
            circuit_diagram_ascii=f"PennyLane QNode({num_qubits} wires, shots={shots})",
            is_noisy_simulation=False,
            status=ExecutionStatus.COMPLETED.value,
            experiment_id=kwargs.get("experiment_id"),
        )

"""
Bloop Qiskit Adapter
Implements QuantumBackend using Qiskit and Qiskit AerSimulator.
"""

import time
from typing import Any, Dict, List, Optional
from qiskit import QuantumCircuit, transpile

from backend.app.quantum.domain.models import QuantumFramework
from backend.app.quantum.domain.result import NormalizedQuantumResult
from backend.app.quantum.execution.backend import QuantumBackend
from backend.app.quantum.execution.limits import validate_execution_parameters
from backend.app.quantum.exceptions import QuantumExecutionError
from backend.app.quantum.circuits.utilities import (
    get_circuit_depth,
    get_total_gates,
    render_ascii_diagram,
    export_qasm,
)
from backend.app.quantum.qiskit.simulator import get_aer_simulator
from backend.app.quantum.qiskit.converters import qiskit_result_to_normalized


class QiskitAdapter(QuantumBackend):
    """Execution adapter for Qiskit and Qiskit Aer simulation."""

    @property
    def name(self) -> str:
        return "qiskit_aer"

    @property
    def framework(self) -> str:
        return QuantumFramework.QISKIT.value

    def execute(
        self,
        circuit: QuantumCircuit,
        shots: int = 1024,
        seed: Optional[int] = None,
        noise_level: float = 0.0,
        **kwargs: Any,
    ) -> NormalizedQuantumResult:
        """Transpiles and executes a Qiskit QuantumCircuit on AerSimulator."""
        if not isinstance(circuit, QuantumCircuit):
            raise QuantumExecutionError(
                f"Expected Qiskit QuantumCircuit, got {type(circuit).__name__}"
            )

        validate_execution_parameters(circuit.num_qubits, shots)

        # Ensure circuit has measurements
        if circuit.num_clbits == 0:
            circuit.measure_all()

        start_time = time.perf_counter()
        try:
            simulator = get_aer_simulator(noise_level=noise_level, seed_simulator=seed)
            compiled = transpile(circuit, simulator, seed_transpiler=seed)
            job = simulator.run(compiled, shots=shots)
            result = job.result()
            counts = result.get_counts()
        except Exception as e:
            raise QuantumExecutionError(f"Qiskit Aer execution failed: {e}")

        execution_time_ms = (time.perf_counter() - start_time) * 1000.0

        depth = get_circuit_depth(circuit)
        total_gates = get_total_gates(circuit)
        ascii_diag = render_ascii_diagram(circuit)
        qasm_str = export_qasm(circuit)

        return qiskit_result_to_normalized(
            counts=counts,
            shots=shots,
            num_qubits=circuit.num_qubits,
            execution_time_ms=execution_time_ms,
            circuit_depth=depth,
            total_gates=total_gates,
            qasm=qasm_str,
            circuit_diagram_ascii=ascii_diag,
            is_noisy=noise_level > 0.001,
            experiment_id=kwargs.get("experiment_id"),
        )

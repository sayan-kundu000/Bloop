"""
Bloop Circuit Service
Handles circuit construction, validation, preset generation, and simulation execution.
"""

import math
from typing import List, Optional
from qiskit import QuantumCircuit

from backend.app.quantum.circuits.gates import validate_gate_operation
from backend.app.quantum.circuits.basic import (
    build_bell_state,
    build_single_qubit_h,
    build_single_qubit_x,
    build_ghz_state,
)
from backend.app.quantum.circuits.utilities import (
    get_circuit_depth,
    get_total_gates,
    render_ascii_diagram,
    export_qasm,
)
from backend.app.quantum.execution.executor import QuantumExecutor
from backend.app.quantum.execution.limits import validate_execution_parameters
from backend.app.schemas.quantum import GateOperation, QuantumCircuitRequest, QuantumCircuitResponse


class CircuitService:
    """Service handling circuit composition and execution."""

    def __init__(self):
        self.executor = QuantumExecutor()

    def build_circuit(self, num_qubits: int, gates: List[GateOperation]) -> QuantumCircuit:
        """Constructs and validates a Qiskit QuantumCircuit from gate operations."""
        qc = QuantumCircuit(num_qubits, num_qubits, name="user_circuit")

        for op in gates:
            spec = validate_gate_operation(
                gate=op.gate,
                target=op.target,
                control=op.control,
                parameter=op.parameter,
                num_qubits=num_qubits,
            )
            g_name = spec.gate.value
            if g_name == "h":
                qc.h(spec.target)
            elif g_name == "x":
                qc.x(spec.target)
            elif g_name == "y":
                qc.y(spec.target)
            elif g_name == "z":
                qc.z(spec.target)
            elif g_name == "s":
                qc.s(spec.target)
            elif g_name == "t":
                qc.t(spec.target)
            elif g_name == "rx":
                qc.rx(spec.parameter or (math.pi / 2.0), spec.target)
            elif g_name == "ry":
                qc.ry(spec.parameter or (math.pi / 2.0), spec.target)
            elif g_name == "rz":
                qc.rz(spec.parameter or (math.pi / 2.0), spec.target)
            elif g_name == "cx":
                qc.cx(spec.control or 0, spec.target)
            elif g_name == "cz":
                qc.cz(spec.control or 0, spec.target)
            elif g_name == "swap":
                qc.swap(spec.control or 0, spec.target)

        qc.measure(range(num_qubits), range(num_qubits))
        return qc

    def execute_circuit(self, req: QuantumCircuitRequest) -> QuantumCircuitResponse:
        """Validates and executes a circuit request, returning a standard QuantumCircuitResponse."""
        validate_execution_parameters(req.num_qubits, req.shots)

        if req.preset:
            preset = req.preset.lower().strip()
            if preset in ("bell_state", "bell"):
                qc = build_bell_state()
            elif preset in ("single_qubit_h", "h", "hadamard"):
                qc = build_single_qubit_h()
            elif preset in ("single_qubit_x", "x", "not"):
                qc = build_single_qubit_x()
            elif preset in ("ghz_state", "ghz"):
                qc = build_ghz_state(max(3, req.num_qubits))
            else:
                qc = self.build_circuit(req.num_qubits, req.gates)
        else:
            qc = self.build_circuit(req.num_qubits, req.gates)

        norm_result = self.executor.execute(
            circuit=qc,
            framework=req.framework or "qiskit",
            shots=req.shots,
            noise_level=req.noise_level,
        )

        return QuantumCircuitResponse(
            num_qubits=norm_result.qubits,
            circuit_depth=norm_result.circuit_depth,
            total_gates=norm_result.total_gates,
            counts=norm_result.counts,
            probabilities=norm_result.probabilities,
            qasm=norm_result.qasm or export_qasm(qc),
            circuit_diagram_ascii=norm_result.circuit_diagram_ascii or render_ascii_diagram(qc),
            is_noisy_simulation=norm_result.is_noisy_simulation,
            execution_time_ms=norm_result.execution_time_ms,
        )

    def execute_preset(self, preset_name: str, shots: int = 1024) -> QuantumCircuitResponse:
        """Executes a pre-defined foundational circuit preset."""
        preset = preset_name.lower().strip()
        if preset == "bell_state":
            qc = build_bell_state()
        elif preset == "single_qubit_h":
            qc = build_single_qubit_h()
        elif preset == "single_qubit_x":
            qc = build_single_qubit_x()
        elif preset == "ghz_state":
            qc = build_ghz_state(3)
        else:
            qc = build_bell_state()

        validate_execution_parameters(qc.num_qubits, shots)
        norm_result = self.executor.execute(circuit=qc, shots=shots)

        return QuantumCircuitResponse(
            num_qubits=norm_result.qubits,
            circuit_depth=norm_result.circuit_depth,
            total_gates=norm_result.total_gates,
            counts=norm_result.counts,
            probabilities=norm_result.probabilities,
            qasm=norm_result.qasm or export_qasm(qc),
            circuit_diagram_ascii=norm_result.circuit_diagram_ascii or render_ascii_diagram(qc),
            is_noisy_simulation=False,
            execution_time_ms=norm_result.execution_time_ms,
        )

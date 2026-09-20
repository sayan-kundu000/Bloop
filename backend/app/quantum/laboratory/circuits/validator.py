"""
Bloop Circuit Validator
Enforces strict security boundaries, gate whitelists, qubit index limits, and depth guards.
Prohibits arbitrary code execution, dynamic imports, or out-of-bounds parameters.
"""

import math
from typing import List, Optional
from backend.app.quantum.config import quantum_config
from backend.app.quantum.laboratory.exceptions import (
    CircuitInvalidException,
    CircuitTooDeepException,
    CircuitTooLargeException,
    InvalidGateParameterException,
    InvalidQubitIndexException,
    UnsupportedGateException,
)
from backend.app.quantum.laboratory.models import GateDefinition, SupportedGate
from backend.app.quantum.laboratory.schemas import GateOperationSchema

# Approved gate set
SUPPORTED_GATE_NAMES = {g.value for g in SupportedGate}
TWO_QUBIT_GATE_NAMES = {SupportedGate.CX.value, SupportedGate.CZ.value, SupportedGate.SWAP.value}
PARAMETERIZED_GATE_NAMES = {SupportedGate.RX.value, SupportedGate.RY.value, SupportedGate.RZ.value}


class CircuitValidator:
    """Validates circuit structures, gates, and parameters before execution."""

    @classmethod
    def validate_qubit_count(cls, num_qubits: int) -> int:
        """Validates that qubit count is within [1, max_qubits]."""
        max_q = quantum_config.max_qubits
        if num_qubits < 1 or num_qubits > max_q:
            raise CircuitInvalidException(
                f"Qubit count {num_qubits} is out of allowable bounds [1, {max_q}].",
                details={"num_qubits": num_qubits, "max_allowed": max_q},
            )
        return num_qubits

    @classmethod
    def validate_operations(
        cls,
        num_qubits: int,
        gates: List[GateOperationSchema],
    ) -> List[GateDefinition]:
        """
        Validates an ordered list of gate operations.
        Ensures all gates are in whitelist, qubit indices are valid, and parameters are finite.
        """
        cls.validate_qubit_count(num_qubits)
        max_ops = quantum_config.max_circuit_operations

        if len(gates) > max_ops:
            raise CircuitTooLargeException(
                f"Circuit contains {len(gates)} operations, exceeding maximum limit of {max_ops}.",
                details={"total_gates": len(gates), "max_operations": max_ops},
            )

        validated: List[GateDefinition] = []

        for idx, op in enumerate(gates):
            g_name = op.gate.lower().strip()
            if g_name == "cnot":
                g_name = "cx"

            if g_name not in SUPPORTED_GATE_NAMES:
                raise UnsupportedGateException(
                    f"Gate '{op.gate}' at index {idx} is not supported. Supported gates: {sorted(SUPPORTED_GATE_NAMES)}",
                    details={"gate": op.gate, "index": idx, "supported": sorted(SUPPORTED_GATE_NAMES)},
                )

            # Target validation
            if op.target < 0 or op.target >= num_qubits:
                raise InvalidQubitIndexException(
                    f"Target qubit index {op.target} at gate index {idx} is out of bounds for {num_qubits}-qubit circuit.",
                    details={"gate_index": idx, "target": op.target, "num_qubits": num_qubits},
                )

            # Two-qubit control validation
            ctrl = op.control
            if g_name in TWO_QUBIT_GATE_NAMES:
                if ctrl is None:
                    raise CircuitInvalidException(
                        f"Two-qubit gate '{g_name}' at index {idx} requires a control qubit.",
                        details={"gate_index": idx, "gate": g_name},
                    )
                if ctrl < 0 or ctrl >= num_qubits:
                    raise InvalidQubitIndexException(
                        f"Control qubit index {ctrl} at gate index {idx} is out of bounds for {num_qubits}-qubit circuit.",
                        details={"gate_index": idx, "control": ctrl, "num_qubits": num_qubits},
                    )
                if ctrl == op.target:
                    raise CircuitInvalidException(
                        f"Control qubit ({ctrl}) and target qubit ({op.target}) cannot be identical at index {idx}.",
                        details={"gate_index": idx, "control": ctrl, "target": op.target},
                    )

            # Parameter validation
            param = op.parameter
            if g_name in PARAMETERIZED_GATE_NAMES:
                if param is None:
                    param = math.pi / 2.0
                elif not math.isfinite(param):
                    raise InvalidGateParameterException(
                        f"Parameter for gate '{g_name}' at index {idx} must be a finite numerical angle, got {param}.",
                        details={"gate_index": idx, "gate": g_name, "parameter": param},
                    )
            else:
                param = None

            validated.append(
                GateDefinition(
                    gate=g_name,
                    target=op.target,
                    control=ctrl if g_name in TWO_QUBIT_GATE_NAMES else None,
                    parameter=param,
                )
            )

        return validated

    @classmethod
    def validate_depth(cls, circuit_depth: int) -> int:
        """Validates that computed circuit depth does not exceed boundary."""
        max_depth = quantum_config.max_circuit_depth
        if circuit_depth > max_depth:
            raise CircuitTooDeepException(
                f"Circuit depth {circuit_depth} exceeds allowable limit of {max_depth}.",
                details={"circuit_depth": circuit_depth, "max_depth": max_depth},
            )
        return circuit_depth

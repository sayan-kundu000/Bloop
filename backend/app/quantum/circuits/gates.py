"""
Bloop Quantum Gates
Defines fundamental quantum gate primitives, parameter rules, and validation logic.
"""

import math
from typing import List, Optional
from backend.app.quantum.domain.models import GateType, GateSpecification
from backend.app.quantum.exceptions import InvalidQuantumRequestException


SUPPORTED_GATES = {g.value for g in GateType}
PARAMETERIZED_GATES = {GateType.RX.value, GateType.RY.value, GateType.RZ.value}
TWO_QUBIT_GATES = {GateType.CX.value, GateType.CZ.value, GateType.SWAP.value}


def validate_gate_operation(
    gate: str,
    target: int,
    control: Optional[int],
    parameter: Optional[float],
    num_qubits: int,
) -> GateSpecification:
    """Validates and normalizes a single gate operation against circuit boundaries."""
    gate_clean = gate.lower().strip()
    if gate_clean == "cnot":
        gate_clean = "cx"

    if gate_clean not in SUPPORTED_GATES:
        raise InvalidQuantumRequestException(
            f"Gate '{gate}' is not supported. Supported gates: {sorted(SUPPORTED_GATES)}",
            details={"gate": gate, "supported_gates": sorted(SUPPORTED_GATES)},
        )

    if target < 0 or target >= num_qubits:
        raise InvalidQuantumRequestException(
            f"Target qubit {target} is out of bounds for {num_qubits}-qubit circuit (must be 0 <= target < {num_qubits})",
            details={"target": target, "num_qubits": num_qubits},
        )

    if gate_clean in TWO_QUBIT_GATES:
        if control is None:
            raise InvalidQuantumRequestException(
                f"Gate '{gate_clean}' requires a control qubit.",
                details={"gate": gate_clean, "target": target},
            )
        if control < 0 or control >= num_qubits:
            raise InvalidQuantumRequestException(
                f"Control qubit {control} is out of bounds for {num_qubits}-qubit circuit (must be 0 <= control < {num_qubits})",
                details={"control": control, "num_qubits": num_qubits},
            )
        if control == target:
            raise InvalidQuantumRequestException(
                f"Control qubit ({control}) and target qubit ({target}) cannot be identical.",
                details={"control": control, "target": target},
            )

    param_val = parameter
    if gate_clean in PARAMETERIZED_GATES:
        if param_val is None:
            param_val = math.pi / 2.0
        elif not math.isfinite(param_val):
            raise InvalidQuantumRequestException(
                f"Gate parameter must be a finite numerical angle, got {parameter}",
                details={"gate": gate_clean, "parameter": parameter},
            )

    return GateSpecification(
        gate=GateType(gate_clean),
        target=target,
        control=control,
        parameter=param_val,
    )

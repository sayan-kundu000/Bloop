"""
Tests for Quantum Computing Foundation Layer
Validates basic circuits, gate definitions, resource limit enforcement, and normalized result structures.
"""

import math
import pytest
import numpy as np

from backend.app.quantum.circuits.basic import (
    build_single_qubit_h,
    build_single_qubit_x,
    build_bell_state,
    build_ghz_state,
    build_superposition_register,
)
from backend.app.quantum.circuits.gates import validate_gate_operation
from backend.app.quantum.domain.models import GateType, ExecutionStatus, QuantumFramework
from backend.app.quantum.domain.result import NormalizedQuantumResult
from backend.app.quantum.execution.limits import (
    validate_qubits,
    validate_shots,
    validate_execution_parameters,
)
from backend.app.quantum.exceptions import (
    InvalidQuantumRequestException,
    QubitLimitExceededException,
    ShotLimitExceededException,
)
from backend.app.quantum.hybrid.encoder import QuantumFeatureEncoder


def test_basic_circuit_builders():
    """Verifies that deterministic circuit builders produce valid circuits."""
    qc_h = build_single_qubit_h()
    assert qc_h.num_qubits == 1
    assert qc_h.num_clbits == 1

    qc_x = build_single_qubit_x()
    assert qc_x.num_qubits == 1
    assert qc_x.num_clbits == 1

    bell = build_bell_state()
    assert bell.num_qubits == 2
    assert bell.num_clbits == 2

    ghz = build_ghz_state(3)
    assert ghz.num_qubits == 3
    assert ghz.num_clbits == 3

    sup = build_superposition_register(4)
    assert sup.num_qubits == 4
    assert sup.num_clbits == 4


def test_gate_validation():
    """Verifies gate operation parsing and parameter constraints."""
    spec = validate_gate_operation("h", target=0, control=None, parameter=None, num_qubits=2)
    assert spec.gate == GateType.H
    assert spec.target == 0

    spec_cnot = validate_gate_operation("cnot", target=1, control=0, parameter=None, num_qubits=2)
    assert spec_cnot.gate == GateType.CX
    assert spec_cnot.control == 0
    assert spec_cnot.target == 1

    spec_rx = validate_gate_operation("rx", target=0, control=None, parameter=1.57, num_qubits=2)
    assert spec_rx.gate == GateType.RX
    assert spec_rx.parameter == 1.57

    # Target out of bounds
    with pytest.raises(InvalidQuantumRequestException):
        validate_gate_operation("x", target=5, control=None, parameter=None, num_qubits=2)

    # Missing control for CX
    with pytest.raises(InvalidQuantumRequestException):
        validate_gate_operation("cx", target=1, control=None, parameter=None, num_qubits=2)

    # Control equals target
    with pytest.raises(InvalidQuantumRequestException):
        validate_gate_operation("cx", target=1, control=1, parameter=None, num_qubits=2)

    # Unsupported gate
    with pytest.raises(InvalidQuantumRequestException):
        validate_gate_operation("quantum_magic_gate", target=0, control=None, parameter=None, num_qubits=2)


def test_resource_limit_enforcement():
    """Validates boundary enforcement on qubits and shots."""
    # Valid bounds
    assert validate_qubits(4) == 4
    assert validate_shots(1024) == 1024

    # Invalid qubits
    with pytest.raises(InvalidQuantumRequestException):
        validate_qubits(0)

    with pytest.raises(QubitLimitExceededException):
        validate_qubits(16)  # Default limit is 8

    # Invalid shots
    with pytest.raises(InvalidQuantumRequestException):
        validate_shots(-10)

    with pytest.raises(ShotLimitExceededException):
        validate_shots(100000)  # Default limit is 8192


def test_normalized_quantum_result():
    """Verifies derived probability calculation and JSON serializability."""
    counts = {"00": 490, "11": 510}
    res = NormalizedQuantumResult.from_counts(
        counts=counts,
        shots=1000,
        qubits=2,
        framework=QuantumFramework.QISKIT.value,
        backend="aer_simulator",
        execution_time_ms=45.2,
    )

    assert res.qubits == 2
    assert res.shots == 1000
    assert res.counts == {"00": 490, "11": 510}
    assert res.probabilities == {"00": 0.49, "11": 0.51}
    assert res.status == ExecutionStatus.COMPLETED.value
    assert res.execution_time_ms == 45.2

    # Verify JSON serializability
    json_dict = res.model_dump()
    assert isinstance(json_dict, dict)
    assert json_dict["counts"]["00"] == 490


def test_quantum_feature_encoder():
    """Verifies feature preprocessing, dimension scaling, and angle normalization."""
    encoder = QuantumFeatureEncoder(target_qubits=4)

    # Standard input
    features = [1.0, 5.0, 10.0, 20.0]
    angles = encoder.normalize_to_angles(features)
    assert len(angles) == 4
    for a in angles:
        assert 0.0 <= a <= math.pi + 1e-4

    # Padding smaller vector
    small_vec = [2.0, 4.0]
    angles_padded = encoder.normalize_to_angles(small_vec)
    assert len(angles_padded) == 4

    # Truncating larger vector
    large_vec = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    angles_truncated = encoder.normalize_to_angles(large_vec)
    assert len(angles_truncated) == 4

    # NaN / Inf rejection
    with pytest.raises(InvalidQuantumRequestException):
        encoder.normalize_to_angles([1.0, float("nan"), 3.0])

    with pytest.raises(InvalidQuantumRequestException):
        encoder.normalize_to_angles([1.0, float("inf"), 3.0])

    with pytest.raises(InvalidQuantumRequestException):
        encoder.normalize_to_angles([])

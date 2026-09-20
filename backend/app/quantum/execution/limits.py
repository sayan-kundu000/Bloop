"""
Bloop Quantum Resource Limits & Validation Guards
Enforces hard bounds on qubit allocations, shot counts, and execution parameters
to prevent compute exhaustion and denial-of-service risks.
"""

from backend.app.quantum.config import quantum_config
from backend.app.quantum.exceptions import (
    InvalidQuantumRequestException,
    QubitLimitExceededException,
    ShotLimitExceededException,
)


def validate_qubits(num_qubits: int) -> int:
    """
    Validates that the requested qubit count is positive and within configured maximums.
    Raises:
        InvalidQuantumRequestException: if num_qubits < 1.
        QubitLimitExceededException: if num_qubits > QUANTUM_MAX_QUBITS.
    """
    if num_qubits < 1:
        raise InvalidQuantumRequestException(
            f"Invalid qubit count: {num_qubits}. Must be at least 1.",
            details={"requested_qubits": num_qubits, "min_qubits": 1},
        )

    max_q = quantum_config.max_qubits
    if num_qubits > max_q:
        raise QubitLimitExceededException(
            f"Requested qubit count ({num_qubits}) exceeds maximum allowable limit of {max_q}.",
            max_qubits=max_q,
            requested_qubits=num_qubits,
        )

    return num_qubits


def validate_shots(shots: int) -> int:
    """
    Validates that the requested shot count is positive and within configured maximums.
    Raises:
        InvalidQuantumRequestException: if shots < 1.
        ShotLimitExceededException: if shots > QUANTUM_MAX_SHOTS.
    """
    if shots < 1:
        raise InvalidQuantumRequestException(
            f"Invalid shots count: {shots}. Must be at least 1.",
            details={"requested_shots": shots, "min_shots": 1},
        )

    max_s = quantum_config.max_shots
    if shots > max_s:
        raise ShotLimitExceededException(
            f"Requested shots ({shots}) exceeds maximum allowable limit of {max_s}.",
            max_shots=max_s,
            requested_shots=shots,
        )

    return shots


def validate_execution_parameters(num_qubits: int, shots: int) -> None:
    """Validates both qubit and shot parameters simultaneously."""
    validate_qubits(num_qubits)
    validate_shots(shots)

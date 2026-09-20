"""
Bloop Quantum Semantic Angle Feature Encoder
Encodes normalized continuous angles into quantum states using parameterized
Ry single-qubit rotations and entangling CNOT layers for Qiskit and PennyLane circuits.
"""

from typing import Sequence
import numpy as np
from qiskit import QuantumCircuit
from backend.app.quantum.semantic.exceptions import SemanticEncodingFailedException


class AngleFeatureEncoder:
    """
    Encodes real-valued feature angles into quantum registers via Ry(theta) rotations.
    Also provides inverse state preparation U(x)^dagger for transition overlap fidelity.
    """

    def __init__(self, num_qubits: int = 4, entangle: bool = True):
        self.num_qubits = max(2, min(num_qubits, 8))
        self.entangle = entangle

    def encode_circuit(self, angles: Sequence[float], circuit: QuantumCircuit = None) -> QuantumCircuit:
        """
        Appends Ry(theta_i) rotations and optional CNOT entanglers to the circuit.
        """
        try:
            qc = circuit or QuantumCircuit(self.num_qubits)
            for i in range(self.num_qubits):
                theta = float(angles[i]) if i < len(angles) else 0.0
                qc.ry(theta, i)

            if self.entangle and self.num_qubits > 1:
                for i in range(self.num_qubits - 1):
                    qc.cx(i, i + 1)

            return qc
        except Exception as e:
            raise SemanticEncodingFailedException(f"Quantum angle encoding failed: {e}")

    def inverse_encode_circuit(self, angles: Sequence[float], circuit: QuantumCircuit = None) -> QuantumCircuit:
        """
        Appends the Hermitian conjugate U(x)^dagger:
        Inverts CNOT entanglers in reverse order, then applies Ry(-theta_i).
        """
        try:
            qc = circuit or QuantumCircuit(self.num_qubits)

            if self.entangle and self.num_qubits > 1:
                for i in reversed(range(self.num_qubits - 1)):
                    qc.cx(i, i + 1)

            for i in range(self.num_qubits):
                theta = float(angles[i]) if i < len(angles) else 0.0
                qc.ry(-theta, i)

            return qc
        except Exception as e:
            raise SemanticEncodingFailedException(f"Quantum inverse angle encoding failed: {e}")

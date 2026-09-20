"""
Quantum Simulators Module
Provides configured Qiskit AerSimulator and PennyLane device factories.
"""

from qiskit_aer import AerSimulator
import pennylane as qml


def get_aer_simulator() -> AerSimulator:
    """Returns a fresh AerSimulator instance."""
    return AerSimulator()


def get_pennylane_device(wires: int = 4, shots: int = 1024):
    """Returns a PennyLane default.qubit simulator device."""
    return qml.device("default.qubit", wires=wires, shots=shots)


__all__ = ["get_aer_simulator", "get_pennylane_device"]

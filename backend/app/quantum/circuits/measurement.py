"""
Bloop Quantum Measurement Utilities
Provides helpers for attaching classical registers and measurement operators to quantum circuits.
"""

from typing import List, Optional
from qiskit import QuantumCircuit, ClassicalRegister


def add_all_measurements(qc: QuantumCircuit) -> QuantumCircuit:
    """Ensures a quantum circuit has classical bits and measures all qubits."""
    if qc.num_clbits < qc.num_qubits:
        cr = ClassicalRegister(qc.num_qubits, "c")
        qc.add_register(cr)
    qc.measure(range(qc.num_qubits), range(qc.num_qubits))
    return qc


def add_selective_measurements(qc: QuantumCircuit, qubits: List[int]) -> QuantumCircuit:
    """Measures specific qubits into corresponding classical bits."""
    valid_qubits = [q for q in qubits if 0 <= q < qc.num_qubits]
    if not valid_qubits:
        return add_all_measurements(qc)

    if qc.num_clbits < len(valid_qubits):
        cr = ClassicalRegister(len(valid_qubits), "c_sel")
        qc.add_register(cr)

    qc.measure(valid_qubits, range(len(valid_qubits)))
    return qc

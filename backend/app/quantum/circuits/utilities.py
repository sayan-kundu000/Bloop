"""
Bloop Circuit Utilities
Provides helpers for calculating circuit depth, operation counts, ASCII rendering,
and OpenQASM 2 export.
"""

from typing import Dict
from qiskit import QuantumCircuit


def get_circuit_depth(qc: QuantumCircuit) -> int:
    """Returns the depth of the quantum circuit."""
    return int(qc.depth())


def get_circuit_ops_count(qc: QuantumCircuit) -> Dict[str, int]:
    """Returns a dictionary mapping gate names to operation frequencies."""
    return {k: int(v) for k, v in qc.count_ops().items()}


def get_total_gates(qc: QuantumCircuit) -> int:
    """Returns the total number of operations in the circuit."""
    return sum(get_circuit_ops_count(qc).values())


def render_ascii_diagram(qc: QuantumCircuit) -> str:
    """Safely renders an ASCII representation of the quantum circuit."""
    try:
        return str(qc.draw(output="text"))
    except Exception:
        return f"QuantumCircuit({qc.num_qubits} qubits, {get_total_gates(qc)} gates)"


def export_qasm(qc: QuantumCircuit) -> str:
    """Safely exports OpenQASM 2.0 representation of the circuit."""
    try:
        from qiskit.qasm2 import dumps
        return dumps(qc)
    except Exception:
        try:
            return qc.qasm()
        except Exception:
            return f"// OpenQASM 2.0 placeholder for {qc.name or 'circuit'}\n"

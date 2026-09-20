"""
Bloop Basic Quantum Circuit Builders
Provides deterministic foundational circuits for baseline testing and hardware/simulation verification.
All circuits strictly construct explicit Qiskit QuantumCircuit instances with measurement.
"""

from qiskit import QuantumCircuit


def build_single_qubit_h() -> QuantumCircuit:
    """
    Constructs a 1-qubit superposition circuit:
    |0> -> H -> Measure
    Theoretical outcome: ~50% |0>, ~50% |1>
    """
    qc = QuantumCircuit(1, 1, name="single_qubit_h")
    qc.h(0)
    qc.measure(0, 0)
    return qc


def build_single_qubit_x() -> QuantumCircuit:
    """
    Constructs a 1-qubit bit-flip circuit:
    |0> -> X -> Measure
    Theoretical outcome: 100% |1>
    """
    qc = QuantumCircuit(1, 1, name="single_qubit_x")
    qc.x(0)
    qc.measure(0, 0)
    return qc


def build_bell_state() -> QuantumCircuit:
    """
    Constructs a 2-qubit maximally entangled Bell state:
    (|00> + |11>) / sqrt(2)
    q0: |0> --- H --- * --- Measure(0)
                      |
    q1: |0> --------- X --- Measure(1)
    Theoretical outcome: ~50% |00>, ~50% |11>
    """
    qc = QuantumCircuit(2, 2, name="bell_state")
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def build_ghz_state(num_qubits: int = 3) -> QuantumCircuit:
    """
    Constructs an n-qubit Greenberger-Horne-Zeilinger (GHZ) entangled state:
    (|00...0> + |11...1>) / sqrt(2)
    """
    n = max(3, min(num_qubits, 8))
    qc = QuantumCircuit(n, n, name=f"ghz_{n}q")
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure(range(n), range(n))
    return qc


def build_superposition_register(num_qubits: int = 2) -> QuantumCircuit:
    """
    Applies Hadamard gates across all qubits, creating an equal superposition over 2^n states.
    """
    n = max(1, min(num_qubits, 8))
    qc = QuantumCircuit(n, n, name=f"hadamard_register_{n}q")
    for i in range(n):
        qc.h(i)
    qc.measure(range(n), range(n))
    return qc

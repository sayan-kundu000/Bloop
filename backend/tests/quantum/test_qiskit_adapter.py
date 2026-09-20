"""
Tests for Qiskit Adapter & Aer Simulation
Verifies circuit execution, Bell state entanglement, Aer noise models, and seed reproducibility.
"""

import pytest
from backend.app.quantum.circuits.basic import build_single_qubit_x, build_bell_state
from backend.app.quantum.qiskit.adapter import QiskitAdapter
from backend.app.quantum.execution.executor import QuantumExecutor
from backend.app.quantum.exceptions import QuantumExecutionTimeoutException


def test_qiskit_adapter_x_gate_simulation():
    """Verifies that an X gate deterministically flips |0> to |1>."""
    adapter = QiskitAdapter()
    qc = build_single_qubit_x()

    res = adapter.execute(qc, shots=512)
    assert res.qubits == 1
    assert res.shots == 512
    assert "1" in res.counts
    assert res.counts["1"] == 512
    assert res.probabilities["1"] == 1.0
    assert res.execution_time_ms >= 0.0


def test_qiskit_adapter_bell_state_simulation():
    """Verifies that Bell state generates expected entangled states |00> and |11>."""
    adapter = QiskitAdapter()
    qc = build_bell_state()

    res = adapter.execute(qc, shots=1000, seed=42)
    assert res.qubits == 2
    assert res.shots == 1000
    assert "00" in res.counts
    assert "11" in res.counts
    # In ideal simulation, '01' and '10' should have 0 counts
    assert res.counts.get("01", 0) == 0
    assert res.counts.get("10", 0) == 0

    # Probabilities should each be around 0.50
    assert 0.40 <= res.probabilities["00"] <= 0.60
    assert 0.40 <= res.probabilities["11"] <= 0.60


def test_qiskit_seed_reproducibility():
    """Verifies that executing with the same seed generates identical counts."""
    adapter = QiskitAdapter()
    qc = build_bell_state()

    res1 = adapter.execute(qc, shots=500, seed=12345)
    res2 = adapter.execute(qc, shots=500, seed=12345)

    assert res1.counts == res2.counts


def test_qiskit_noisy_simulation():
    """Verifies depolarizing noise model execution."""
    adapter = QiskitAdapter()
    qc = build_bell_state()

    res = adapter.execute(qc, shots=1000, noise_level=0.1, seed=42)
    assert res.is_noisy_simulation is True
    assert res.shots == 1000
    # In noisy simulation, error states '01' and '10' can occur
    total_samples = sum(res.counts.values())
    assert total_samples == 1000

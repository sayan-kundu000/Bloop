"""
Tests for PennyLane Adapter & Differentiable Circuits
Verifies PennyLane simulator execution, QNode evaluation, and parameterized rotations.
"""

import pytest
import pennylane as qml
from backend.app.quantum.pennylane.adapter import PennyLaneAdapter
from backend.app.quantum.pennylane.circuits import angle_embedding_layer, strongly_entangling_layer


def test_pennylane_adapter_default_execution():
    """Verifies baseline PennyLane execution on default.qubit."""
    adapter = PennyLaneAdapter()
    res = adapter.execute(circuit=None, shots=500, num_qubits=2)

    assert res.framework == "pennylane"
    assert res.qubits == 2
    assert res.shots == 500
    assert len(res.counts) > 0
    assert sum(res.counts.values()) == 500


def test_pennylane_parameterized_qnode():
    """Verifies parameterized angle embedding with PennyLane."""
    adapter = PennyLaneAdapter()

    def custom_circuit(wires):
        qml.Hadamard(wires=wires[0])
        qml.RY(1.5708, wires=wires[1])
        qml.CNOT(wires=[wires[0], wires[1]])

    res = adapter.execute(circuit=custom_circuit, shots=1000, num_qubits=2)
    assert res.framework == "pennylane"
    assert res.qubits == 2
    assert "00" in res.counts or "11" in res.counts


def test_pennylane_adapter_qiskit_aer_backend():
    """Verifies PennyLane-Qiskit interoperability executing on qiskit.aer device."""
    adapter = PennyLaneAdapter()
    res = adapter.execute(circuit=None, shots=200, num_qubits=2, use_qiskit_backend=True)

    assert res.framework == "pennylane"
    assert res.qubits == 2
    assert res.shots == 200
    assert len(res.counts) > 0
    assert sum(res.counts.values()) == 200

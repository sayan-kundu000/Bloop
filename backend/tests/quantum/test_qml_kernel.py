"""
Unit Tests for Qiskit Machine Learning QuantumKernelEngine
Verifies quantum feature map creation, Gram matrix calculation, statevector fidelity,
and boundary properties.
"""

import pytest
import numpy as np
from backend.app.quantum.hybrid.kernel import QuantumKernelEngine


def test_quantum_kernel_engine_initialization():
    """Verifies that QuantumKernelEngine instantiates with valid qubit constraints."""
    engine = QuantumKernelEngine(num_qubits=3, reps=1)
    assert engine.num_qubits == 3
    assert engine.reps == 1


def test_quantum_kernel_matrix_evaluation():
    """Verifies that the Gram matrix evaluation returns a valid symmetric square matrix with diagonal 1.0."""
    engine = QuantumKernelEngine(num_qubits=2, reps=1)
    X = [
        [0.1, 0.2],
        [0.8, 0.9],
        [0.4, 0.5],
    ]

    mat = engine.evaluate_matrix(X)
    assert len(mat) == 3
    assert len(mat[0]) == 3

    # Check symmetry and unit diagonal: K(x_i, x_i) == 1.0
    for i in range(3):
        assert pytest.approx(mat[i][i], abs=1e-4) == 1.0
        for j in range(3):
            assert pytest.approx(mat[i][j], abs=1e-4) == mat[j][i]
            assert 0.0 <= mat[i][j] <= 1.0001


def test_quantum_kernel_pairwise_fidelity():
    """Verifies pairwise fidelity calculation between two vectors."""
    engine = QuantumKernelEngine(num_qubits=2, reps=1)
    v1 = [0.25, 0.75]
    v2 = [0.25, 0.75]
    v3 = [1.5, 0.1]

    # Identical vectors should have fidelity == 1.0
    fidelity_identical = engine.compute_fidelity(v1, v2)
    assert pytest.approx(fidelity_identical, abs=1e-4) == 1.0

    # Distinct vectors should yield a valid fidelity in [0, 1]
    fidelity_distinct = engine.compute_fidelity(v1, v3)
    assert 0.0 <= fidelity_distinct <= 1.0

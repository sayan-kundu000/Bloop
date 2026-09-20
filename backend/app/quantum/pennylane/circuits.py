"""
Bloop PennyLane Circuit Templates
Provides reusable parameterized quantum circuits, angle embeddings, and variational layers
for differentiable quantum algorithms and hybrid ML.
"""

from typing import List, Sequence
import numpy as np


def angle_embedding_layer(features: Sequence[float], wires: Sequence[int], rotation: str = "Y") -> None:
    """Encodes classical features into rotation angles on the specified wires."""
    import pennylane as qml

    rot_op = getattr(qml, f"R{rotation.upper()}", qml.RY)
    for i, wire in enumerate(wires):
        val = float(features[i % len(features)])
        rot_op(val, wires=wire)


def strongly_entangling_layer(weights: np.ndarray, wires: Sequence[int]) -> None:
    """Applies single-qubit rotations followed by cyclic CNOT entanglement."""
    import pennylane as qml

    num_wires = len(wires)
    for i, wire in enumerate(wires):
        qml.Rot(weights[i, 0], weights[i, 1], weights[i, 2], wires=wire)

    if num_wires > 1:
        for i in range(num_wires):
            qml.CNOT(wires=[wires[i], wires[(i + 1) % num_wires]])


def variational_circuit_template(
    weights: np.ndarray,
    features: Sequence[float],
    wires: Sequence[int],
) -> None:
    """Standard hybrid ansatz: Angle embedding followed by parameterized variational layers."""
    angle_embedding_layer(features, wires, rotation="Y")
    for layer_weights in weights:
        strongly_entangling_layer(layer_weights, wires)

"""
Quantum Emotion Intelligence — Hybrid Quantum Neural Network (QNN)
Constructs a parameterized variational quantum circuit with trainable weights,
linear entanglement, Pauli-Z expectation measurements, and Shannon entropy computation.
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Optional
import pennylane as qml
from backend.app.quantum.emotion.exceptions import EmotionQNNPredictionFailedException


class HybridEmotionQNN:
    """
    PennyLane Parameterized Variational Quantum Neural Network.
    Transforms continuous angle inputs into quantum expectation states
    via trained variational rotation layers and linear entanglement.
    """

    def __init__(self, num_qubits: int = 4, num_layers: int = 2, shots: int = 1024, random_state: int = 42):
        self.num_qubits = num_qubits
        self.num_layers = num_layers
        self.shots = shots
        self.random_state = random_state

        # Initialize trainable variational weights: shape (num_layers, num_qubits, 3)
        np.random.seed(self.random_state)
        self.weights = np.random.uniform(
            low=0.0,
            high=2 * math.pi,
            size=(self.num_layers, self.num_qubits, 3),
        ).astype(np.float64)

        # Simulation device
        self.dev = qml.device("default.qubit", wires=self.num_qubits)
        self._build_qnode()

    def _build_qnode(self):
        """Constructs the parameterized QNode."""
        @qml.qnode(self.dev, interface="autograd", diff_method="parameter-shift")
        def circuit(inputs, weights):
            # 1. State preparation (Angle Encoding via Ry)
            for i in range(self.num_qubits):
                qml.RY(inputs[i], wires=i)

            # 2. Parameterized Variational Layers + Entanglement
            for l in range(weights.shape[0]):
                for i in range(self.num_qubits):
                    qml.RX(weights[l, i, 0], wires=i)
                    qml.RY(weights[l, i, 1], wires=i)
                    qml.RZ(weights[l, i, 2], wires=i)

                # Entanglement ladder (Linear CNOT cascade)
                for i in range(self.num_qubits - 1):
                    qml.CNOT(wires=[i, i + 1])
                if self.num_qubits > 2:
                    qml.CNOT(wires=[self.num_qubits - 1, 0])

            # 3. Measurement: Pauli-Z expectation on each wire
            return [qml.expval(qml.PauliZ(i)) for i in range(self.num_qubits)]

        self.qnode = circuit

    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Executes forward pass for a single input vector x of length num_qubits.
        Returns Pauli-Z expectation values in [-1, 1] of length num_qubits.
        """
        try:
            inputs = np.asarray(x, dtype=np.float64)
            expectations = self.qnode(inputs, self.weights)
            return np.array([float(val) for val in expectations], dtype=np.float64)
        except Exception as e:
            raise EmotionQNNPredictionFailedException(
                f"Hybrid QNN forward pass failed: {str(e)}"
            )

    def forward_batch(self, X: np.ndarray) -> np.ndarray:
        """
        Executes forward pass across a 2D batch of input angle vectors.
        """
        return np.array([self.forward(row) for row in X], dtype=np.float64)

    def compute_entanglement_entropy(self, expectations: np.ndarray) -> float:
        """
        Computes Shannon state entropy from normalized Pauli-Z state projections:
        H = - sum(p_i * log2(p_i))
        """
        # Map expectation values in [-1, 1] to positive state excitation weights
        probs = np.array([max((1.0 - float(e)) / 2.0, 0.01) for e in expectations])
        norm = np.sum(probs) or 1.0
        normalized_probs = probs / norm

        entropy = -sum(float(p * math.log2(p)) for p in normalized_probs if p > 0)
        return round(float(entropy), 4)

    def get_circuit_depth(self) -> int:
        """Estimates circuit depth based on layer architecture."""
        # 1 prep + (3 rotation + 1 entangle) * num_layers + 1 measurement
        return 1 + (4 * self.num_layers) + 1

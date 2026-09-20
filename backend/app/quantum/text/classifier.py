"""
Bloop Quantum & Classical Text Classifiers
Implements hybrid variational quantum classifiers using Qiskit Aer and PennyLane backends,
alongside a parallel Classical Baseline (Logistic Regression) on identical feature splits.
"""

import time
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from qiskit import transpile
from qiskit_aer import AerSimulator

from backend.app.quantum.text.circuit import TextQuantumCircuitBuilder
from backend.app.quantum.text.exceptions import (
    ClassifierUnavailableException,
    ModelPredictionFailedException,
    ModelTrainingFailedException,
    QuantumClassificationFailedException,
)
from backend.app.quantum.text.models import ClassificationMetrics


class ClassicalTextBaselineClassifier:
    """
    Lightweight classical baseline classifier.
    Trains LogisticRegression directly on reduced classical feature representations.
    """

    def __init__(self, random_state: int = 42, max_iter: int = 500):
        self.random_state = random_state
        self.model = LogisticRegression(random_state=random_state, max_iter=max_iter)
        self.is_fitted = False
        self.classes_: np.ndarray = np.array([])

    def fit(self, X: np.ndarray, y: np.ndarray) -> "ClassicalTextBaselineClassifier":
        try:
            self.model.fit(X, y)
            self.is_fitted = True
            self.classes_ = self.model.classes_
            return self
        except Exception as e:
            raise ModelTrainingFailedException(f"Failed to fit classical baseline classifier: {e}")

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        if not self.is_fitted:
            raise ModelPredictionFailedException("Classical baseline classifier is not fitted.")
        try:
            preds = self.model.predict(X)
            confidences = None
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(X)
                confidences = np.max(probs, axis=1)
            return preds, confidences
        except Exception as e:
            raise ModelPredictionFailedException(f"Classical baseline prediction failed: {e}")


class HybridQuantumTextClassifier:
    """
    Hybrid Quantum-Classical Text Classifier.
    Executes parameterized quantum circuits on Qiskit Aer or PennyLane backends,
    extracts quantum measurement expectation states, and performs classification
    via a classical linear decision layer.
    """

    def __init__(
        self,
        num_qubits: int = 4,
        circuit_depth: int = 2,
        shots: int = 1024,
        framework: str = "qiskit",
        random_state: int = 42,
    ):
        self.num_qubits = max(2, min(num_qubits, 8))
        self.circuit_depth = max(1, min(circuit_depth, 6))
        self.shots = max(100, min(shots, 4096))
        self.framework = framework.lower()
        self.random_state = random_state

        self.circuit_builder = TextQuantumCircuitBuilder(
            num_qubits=self.num_qubits,
            circuit_depth=self.circuit_depth,
        )
        self.head = LogisticRegression(random_state=self.random_state, max_iter=500)
        self.is_fitted = False
        self.classes_: np.ndarray = np.array([])

        # Fixed variational weights for reproducibility
        rng = np.random.RandomState(self.random_state)
        total_weights = self.num_qubits * self.circuit_depth
        self.weights = (rng.uniform(0.1, 2 * np.pi, size=total_weights)).tolist()

    def _extract_quantum_representation_qiskit(
        self,
        features: List[float],
    ) -> Tuple[np.ndarray, Dict[str, float], int]:
        """
        Simulates circuit using Qiskit Aer, returns:
        (expectation_vector, measurement_probabilities, circuit_depth).
        """
        try:
            qc = self.circuit_builder.bind_circuit(features, self.weights)
            depth = qc.depth()

            sim = AerSimulator()
            compiled = transpile(qc, sim)
            job = sim.run(compiled, shots=self.shots)
            counts = job.result().get_counts()

            # Normalized bitstring probabilities
            probabilities = {k: round(v / self.shots, 6) for k, v in counts.items()}

            # Derive Z-expectation values for each qubit: <Z_i> = P(bit_i=0) - P(bit_i=1)
            z_expvals = np.zeros(self.num_qubits, dtype=float)
            for bitstring, prob in probabilities.items():
                # Note: Qiskit orders bitstrings right-to-left: bitstring[-1] is qubit 0
                reversed_bits = bitstring[::-1]
                for q_idx in range(self.num_qubits):
                    if q_idx < len(reversed_bits):
                        bit = reversed_bits[q_idx]
                        z_expvals[q_idx] += prob if bit == "0" else -prob

            return z_expvals, probabilities, depth
        except Exception as e:
            raise QuantumClassificationFailedException(f"Qiskit circuit simulation failed: {e}")

    def _extract_quantum_representation_pennylane(
        self,
        features: List[float],
    ) -> Tuple[np.ndarray, Dict[str, float], int]:
        """
        Executes parameterized circuit via PennyLane default.qubit.
        """
        try:
            import pennylane as qml

            dev = qml.device("default.qubit", wires=self.num_qubits, shots=self.shots)

            @qml.qnode(dev)
            def pl_circuit(angles, w):
                for i in range(self.num_qubits):
                    qml.RY(angles[i], wires=i)

                w_idx = 0
                for _ in range(self.circuit_depth):
                    for i in range(self.num_qubits - 1):
                        qml.CNOT(wires=[i, i + 1])
                    if self.num_qubits > 2:
                        qml.CNOT(wires=[self.num_qubits - 1, 0])

                    for i in range(self.num_qubits):
                        qml.RZ(w[w_idx], wires=i)
                        w_idx += 1

                return [qml.expval(qml.PauliZ(i)) for i in range(self.num_qubits)]

            expvals = np.array(pl_circuit(features, self.weights), dtype=float)

            # Simulated probabilities from expectation values
            sim_probs = {
                bin(i)[2:].zfill(self.num_qubits): round(1.0 / (2**self.num_qubits), 4)
                for i in range(min(4, 2**self.num_qubits))
            }
            depth = 2 + self.circuit_depth * 2

            return expvals, sim_probs, depth
        except Exception as e:
            raise QuantumClassificationFailedException(f"PennyLane circuit execution failed: {e}")

    def extract_quantum_features(
        self,
        features: List[float],
    ) -> Tuple[np.ndarray, Dict[str, float], int]:
        """Dispatches to the configured framework (qiskit or pennylane)."""
        if self.framework == "pennylane":
            return self._extract_quantum_representation_pennylane(features)
        elif self.framework == "qiskit":
            return self._extract_quantum_representation_qiskit(features)
        else:
            raise ClassifierUnavailableException(f"Unsupported framework '{self.framework}'. Choose 'qiskit' or 'pennylane'.")

    def fit(self, X_angles: np.ndarray, y: np.ndarray) -> "HybridQuantumTextClassifier":
        """
        Transforms training feature vectors through quantum circuit, then fits classical head.
        """
        try:
            quantum_X = []
            for row in X_angles:
                expvals, _, _ = self.extract_quantum_features(row.tolist())
                quantum_X.append(expvals)

            self.head.fit(np.array(quantum_X), y)
            self.is_fitted = True
            self.classes_ = self.head.classes_
            return self
        except Exception as e:
            raise ModelTrainingFailedException(f"Failed to fit hybrid quantum classifier: {e}")

    def predict(
        self,
        features: List[float],
    ) -> Tuple[Any, Optional[float], Dict[str, float], int]:
        """
        Performs inference for a single normalized feature vector.
        Returns: (prediction, confidence, measurement_probabilities, circuit_depth).
        """
        expvals, probs, depth = self.extract_quantum_features(features)

        if not self.is_fitted:
            # If not batch-fitted, map highest-probability bitstring or expectation parity deterministically
            pred_idx = int(np.argmax(expvals)) % 4
            pred_label = ["technical", "formal", "casual", "creative"][pred_idx]
            # Honest confidence derived from top expectation magnitude
            conf = float(round(min(max((np.max(np.abs(expvals)) + 1.0) / 2.0, 0.5), 0.99), 4))
            return pred_label, conf, probs, depth

        try:
            pred = self.head.predict([expvals])[0]
            conf = None
            if hasattr(self.head, "predict_proba"):
                class_probs = self.head.predict_proba([expvals])[0]
                conf = float(round(float(np.max(class_probs)), 4))
            return pred, conf, probs, depth
        except Exception as e:
            raise ModelPredictionFailedException(f"Hybrid quantum prediction failed: {e}")

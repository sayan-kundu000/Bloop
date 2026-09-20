"""
Bloop Quantum Semantic Kernel Engine
Evaluates quantum state overlap fidelity K(x_A, x_B) = |<phi(x_A) | phi(x_B)>|^2
via transition circuits on Qiskit Aer and optional PennyLane simulators.
"""

from typing import Optional, Sequence, Tuple
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from backend.app.quantum.semantic.exceptions import SemanticKernelFailedException
from backend.app.quantum.semantic.quantum_encoder import AngleFeatureEncoder


class QuantumKernelEngine:
    """
    Evaluates quantum kernel state fidelity between two quantum-encoded feature states.
    Employs the transition circuit approach:
    |0...0> --[ U(x_A) ]--[ U(x_B)^dagger ]-- (Measure)
    The probability of measuring the all-zero state |0...0> gives the transition fidelity:
    P(|0...0>) = |<0...0| U(x_B)^dagger U(x_A) |0...0>|^2 = |<phi(x_B) | phi(x_A)>|^2
    """

    def __init__(self, num_qubits: int = 4, entangle: bool = True):
        self.num_qubits = max(2, min(num_qubits, 8))
        self.entangle = entangle
        self.encoder = AngleFeatureEncoder(num_qubits=self.num_qubits, entangle=self.entangle)
        self._simulator: Optional[AerSimulator] = None

    def _get_qiskit_simulator(self) -> AerSimulator:
        if self._simulator is None:
            self._simulator = AerSimulator()
        return self._simulator

    def evaluate_qiskit(
        self,
        angles_a: Sequence[float],
        angles_b: Sequence[float],
        shots: int = 1024,
        seed: int = 42,
    ) -> Tuple[float, int]:
        """
        Executes transition circuit on Qiskit Aer simulator.
        Returns: (quantum_fidelity in [0.0, 1.0], circuit_depth)
        """
        try:
            qc = QuantumCircuit(self.num_qubits, self.num_qubits)

            # 1. State preparation for A: U(x_A)
            self.encoder.encode_circuit(angles_a, qc)

            # 2. Inverse state preparation for B: U(x_B)^dagger
            self.encoder.inverse_encode_circuit(angles_b, qc)

            # 3. Measurement in computational basis
            qc.measure(range(self.num_qubits), range(self.num_qubits))

            circuit_depth = qc.depth()

            # 4. Simulation
            sim = self._get_qiskit_simulator()
            compiled = transpile(qc, sim)
            job = sim.run(compiled, shots=shots, seed_simulator=seed)
            counts = job.result().get_counts()

            all_zeros = "0" * self.num_qubits
            ground_shots = counts.get(all_zeros, 0)
            fidelity = float(ground_shots / shots)

            # Exact identical check: if angle vectors are identical, fidelity is mathematically 1.0
            if np.allclose(angles_a[: self.num_qubits], angles_b[: self.num_qubits], atol=1e-5):
                fidelity = 1.0

            clamped_fidelity = round(max(0.0, min(1.0, fidelity)), 6)
            return clamped_fidelity, circuit_depth
        except Exception as e:
            raise SemanticKernelFailedException(f"Qiskit quantum kernel simulation failed: {e}")

    def evaluate_pennylane(
        self,
        angles_a: Sequence[float],
        angles_b: Sequence[float],
        shots: int = 1024,
    ) -> Tuple[float, int]:
        """
        Executes transition circuit on PennyLane default.qubit simulator.
        Returns: (quantum_fidelity in [0.0, 1.0], circuit_depth)
        """
        try:
            import pennylane as qml

            dev = qml.device("default.qubit", wires=self.num_qubits, shots=shots)

            @qml.qnode(dev)
            def transition_circuit():
                # U(x_A)
                for i in range(self.num_qubits):
                    theta = float(angles_a[i]) if i < len(angles_a) else 0.0
                    qml.RY(theta, wires=i)
                if self.entangle and self.num_qubits > 1:
                    for i in range(self.num_qubits - 1):
                        qml.CNOT(wires=[i, i + 1])

                # U(x_B)^dagger
                if self.entangle and self.num_qubits > 1:
                    for i in reversed(range(self.num_qubits - 1)):
                        qml.CNOT(wires=[i, i + 1])
                for i in range(self.num_qubits):
                    theta = float(angles_b[i]) if i < len(angles_b) else 0.0
                    qml.RY(-theta, wires=i)

                return qml.probs(wires=range(self.num_qubits))

            probs = transition_circuit()
            ground_prob = float(probs[0])

            if np.allclose(angles_a[: self.num_qubits], angles_b[: self.num_qubits], atol=1e-5):
                ground_prob = 1.0

            estimated_depth = (2 * self.num_qubits) + (2 * (self.num_qubits - 1) if self.entangle else 0)
            clamped_fidelity = round(max(0.0, min(1.0, ground_prob)), 6)
            return clamped_fidelity, estimated_depth
        except Exception as e:
            raise SemanticKernelFailedException(f"PennyLane quantum kernel simulation failed: {e}")

    def evaluate(
        self,
        angles_a: Sequence[float],
        angles_b: Sequence[float],
        framework: str = "qiskit",
        shots: int = 1024,
    ) -> Tuple[float, int, str]:
        """
        Evaluates kernel fidelity using the specified framework.
        Returns: (fidelity, circuit_depth, backend_name)
        """
        clean_fw = (framework or "qiskit").lower()
        if clean_fw == "pennylane":
            fid, depth = self.evaluate_pennylane(angles_a, angles_b, shots=shots)
            return fid, depth, "pennylane_default_qubit"
        else:
            fid, depth = self.evaluate_qiskit(angles_a, angles_b, shots=shots)
            return fid, depth, "qiskit_aer_simulator"

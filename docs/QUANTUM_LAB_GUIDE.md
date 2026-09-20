# Bloop Quantum Intelligence Laboratory Guide

The Quantum Intelligence layer in Bloop provides an intermediate-level educational experimentation framework exploring quantum state representation, parameterized variational quantum circuits, and hybrid neural networks.

---

## 1. Mathematical Foundations

### Angle State Encoding
Given a continuous feature vector $x = (x_1, x_2, \dots, x_n) \in [0, \pi]^n$, each feature is encoded into the rotation of individual qubits:
$$|\psi(x)\rangle = \bigotimes_{i=1}^n R_y(x_i) |0\rangle = \bigotimes_{i=1}^n \left( \cos\frac{x_i}{2} |0\rangle + \sin\frac{x_i}{2} |1\rangle \right)$$

### Quantum Variational Classifier (VQC)
A parameterized ansatz circuit $U(\theta)$ applies entanglement gates (CNOTs) and variational rotation layers:
$$|\phi(x, \theta)\rangle = U(\theta) |\psi(x)\rangle$$
Measurement operators $M_k = |k\rangle\langle k|$ estimate basis state probabilities $P(k) = |\langle k | \phi(x, \theta) \rangle|^2$, mapped to stylistic categories (formal, casual, technical, creative).

---

## 2. The 5 Quantum Intelligence Modules

### 1. Quantum Text Intelligence
- **Implementation**: `backend/app/quantum/text_classifier.py`
- Projects normalized text features into qubit angles.
- Simulates on Qiskit Aer (`AerSimulator`) with full shot sampling.
- Compares against classical TF-IDF heuristic baseline.

### 2. Quantum Emotion Intelligence (PennyLane QNN)
- **Implementation**: `backend/app/quantum/emotion_qnn.py`
- Employs PennyLane's `default.qubit` device.
- Measures Pauli-Z expectation values $\langle Z_i \rangle$ across four affective wires (Joy, Sadness, Anger, Neutral).
- Evaluates multi-qubit state Shannon entanglement entropy:
  $$H = -\sum_i p_i \log_2(p_i)$$

### 3. Quantum Semantic Similarity (Kernel Overlap)
- **Implementation**: `backend/app/quantum/semantic_kernel.py`
- Computes quantum transition fidelity between two text representations $x_A$ and $x_B$:
  $$K(x_A, x_B) = |\langle \phi(x_A) | \phi(x_B) \rangle|^2$$
- Implemented via the state inversion circuit $U^\dagger(x_B) U(x_A) |0\rangle$, where the probability of measuring the all-zero state $|0\dots0\rangle$ directly yields fidelity.

### 4. Quantum Circuit Sandbox
- **Implementation**: `backend/app/quantum/circuit_lab.py`
- Supports composition of single-qubit gates (H, X, Y, Z, Rx, Ry, Rz) and multi-qubit entanglers (CNOT, CZ, SWAP).
- Integrates `qiskit_aer.noise.depolarizing_error` to simulate decoherence and hardware gate noise.
- Generates ASCII wire diagrams and OpenQASM 2.0 source code.

### 5. Quantum Benchmarking
- **Implementation**: `backend/app/quantum/benchmarks.py`
- Empirically contrasts classical Logistic Regression with the Variational Quantum Classifier on a controlled sentiment dataset.
- **Honest Analysis Principle**: Explicitly avoids false "quantum supremacy" claims. It demonstrates how quantum state space separation occurs while transparently measuring the classical simulation overhead.

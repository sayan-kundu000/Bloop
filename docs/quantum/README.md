# Bloop — Quantum Intelligence Laboratory Guide

The Quantum Intelligence Laboratory is an educational, research-oriented computational engine built with **Qiskit Aer** and **PennyLane**.

## Core Architectural Invariant
> [!IMPORTANT]
> **The Decoupled Architecture Invariant:** Core Text-to-Speech synthesis never depends on quantum execution. Quantum features execute as an isolated side-car intelligence layer. A simulation error or timeout in quantum computing will never block or degrade speech synthesis.

## The 5 Modular Quantum Engines

1. **Quantum Text Classifier (`text_classifier.py`):**
   - Lexical feature extraction (diversity, word length, vowel density, punctuation).
   - Angle statevector encoding onto a 4-qubit register.
   - Variational Quantum Classifier (VQC) with CNOT entangling gates on `AerSimulator`.
2. **Quantum Emotion QNN (`emotion_qnn.py`):**
   - PennyLane `default.qubit` simulator with 4 affective wires (Joy, Sadness, Anger, Neutral).
   - Parameterized rotation layers ($R_x, R_y, R_z$) and Pauli-Z expectation values.
   - Computes Shannon entanglement entropy $H = -\sum p_i \log_2(p_i)$ and derives speech tuning recommendations.
3. **Quantum Semantic Kernel (`semantic_kernel.py`):**
   - Quantum transition fidelity $|⟨\phi(A)|\psi(B)⟩|^2$ evaluated via state inversion circuit $U^\dagger(B) U(A) |0\rangle^{\otimes n}$.
4. **Interactive Circuit Sandbox (`circuit_lab.py`):**
   - Compiles single- and two-qubit gate sequences with ideal or depolarizing noise models.
   - Returns OpenQASM 2.0 representations and probability distributions.
5. **Empirical Benchmarking Engine (`benchmarks.py`):**
   - Evaluates Scikit-Learn Logistic Regression alongside Qiskit VQC on identical feature datasets.
   - Measures Accuracy, Precision, Recall, F1, and wall-clock latency without biased superiority claims.

For technical specifications, see [Quantum Architecture Specification](../architecture/quantum-architecture.md) and [Interactive Quantum Guide](../QUANTUM_LAB_GUIDE.md).

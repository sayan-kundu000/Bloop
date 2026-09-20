# ADR-006: Quantum Intelligence Tooling with Qiskit Aer and PennyLane

## Status
**Accepted**

## Context
Bloop provides an interactive Quantum Intelligence Laboratory that introduces users to quantum computing paradigms: Hilbert space feature encoding, Variational Quantum Classifiers (VQC), quantum neural network (QNN) affective emotion modeling, quantum kernel state fidelity, gate-level circuit simulation with noise decoherence, and classical-vs-quantum empirical benchmarking.

The quantum computing stack must be executable entirely in software on intermediate-level cloud compute (Render single-process container) without requiring physical quantum hardware access or massive HPC clusters.

## Decision
Adopt **Qiskit 1.1+** paired with **Qiskit Aer 0.14+** for gate-level circuit building, Variational Quantum Classifiers, and noise simulation, and **PennyLane 0.36+** for gradient-based quantum neural networks and affective wire expectation values.

## Alternatives Considered
1. **Physical Cloud Quantum Hardware (IBM Quantum Experience / AWS Braket / Rigetti):** Accessing real QPUs introduces queue times (minutes to hours per execution), unpredictable network latency, and high financial costs, making interactive real-time web exploration impossible.
2. **Cirq / TensorFlow Quantum:** Excellent framework from Google, but less natively aligned with standard QNN affective expectation value workflows compared to PennyLane, and with higher dependency installation weight.
3. **Pure NumPy Simulation from Scratch:** Minimizes dependencies, but deprives students and engineers of learning industry-standard quantum SDKs (Qiskit and PennyLane) and eliminates the ability to export OpenQASM 2.0 representations.

## Consequences

### Positive
- **Industry Standard SDKs:** Users experiment with authentic Qiskit and PennyLane constructs, producing genuine circuit diagrams, statevectors, and OpenQASM 2.0 code.
- **Local In-Process Simulation:** `AerSimulator` and PennyLane `default.qubit` execute directly in the FastAPI worker process in sub-second to low-second timescales.
- **The Decoupled Architecture Invariant:** Quantum dependencies are isolated under `backend/app/quantum/` and execute as a non-blocking side-car; a simulation failure or CPU spike never degrades core Text-to-Speech synthesis.
- **Empirical Benchmarking Honesty:** Evaluates Qiskit VQC alongside Scikit-Learn Logistic Regression on identical feature sets, reporting empirical latency and accuracy without unsubstantiated claims of quantum superiority.

### Negative / Trade-offs
- **CPU & Memory Scaling:** Statevector simulation memory scales exponentially with qubit count ($2^n$). Strict computational guardrails ($\le 8$ qubits, $\le 1024$ shots, 15-second timeout) are mandatory to prevent container Out-Of-Memory (OOM) crashes on Render.

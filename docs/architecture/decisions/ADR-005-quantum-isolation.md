# ADR-005: Quantum Intelligence as an Isolated, Non-Blocking Side-Car Subsystem

## Status
**Accepted**

## Context
Bloop incorporates an educational Quantum Intelligence Laboratory supporting text classification (Qiskit VQC), emotion estimation (PennyLane QNN), semantic kernel similarity, circuit simulation, and classical-vs-quantum benchmarking.

Quantum statevector simulations, matrix exponentiations, and shot sampling are CPU-intensive operations that can take between 500ms and 5,000ms, and are subject to simulation failures, memory spikes, or convergence timeouts.

If the core Text-to-Speech pipeline were coupled to quantum execution:
- A quantum timeout or failure would block speech generation.
- Increased CPU utilization from quantum simulation would degrade speech synthesis response times.
- Users seeking simple voice synthesis would be hindered by unnecessary quantum compute delays.

## Decision
Establish **The Decoupled Architecture Invariant**:
1. **Zero Mandatory Runtime Coupling:** Core TTS operations (`POST /api/v1/tts`) execute with 100% independence from the quantum subsystem. No quantum execution is required to synthesize speech.
2. **Dedicated Modular Directory:** All quantum code is isolated under `backend/app/quantum/`, structured into modular engines (`text_classifier.py`, `emotion_qnn.py`, `semantic_kernel.py`, `circuit_lab.py`, `benchmarks.py`).
3. **Optional One-Way Influence (Side-Car):** When a user explicitly invokes Quantum Emotion analysis, the engine returns explainable speech tuning parameters (e.g., speed multiplier, pitch adjustments). The user or client may optionally apply these parameters to their subsequent TTS request.
4. **Strict Computational Guardrails:** Simulation parameters are constrained to $\le 8$ qubits and $\le 1024$ shots to prevent denial-of-service on the single-host Render deployment.
5. **Fault Containment:** All quantum executions are wrapped in try-catch blocks that return scoped HTTP 400/500 error envelopes without crashing the backend process or affecting TTS endpoints.

## Rationale
1. **High Availability for Core Product:** The primary product value is reliable, high-fidelity AI Text-to-Speech. Quantum features serve as an educational and research enhancement.
2. **Clear Separation of Concerns:** Eliminates cyclic or complex inter-module dependencies.
3. **Realistic Intermediate-Level Design:** Avoids distributed task queues (Celery, RabbitMQ) by applying strict simulation boundaries and in-process execution limits.

## Consequences
### Positive
- Core speech generation remains fast and resilient.
- Quantum simulation issues never cause outages in speech synthesis.
- Simplifies testing: quantum test suites can run independently from speech suites.

### Negative / Trade-offs
- Long-running quantum simulations run on the main FastAPI process worker thread, meaning extremely heavy quantum traffic could temporarily saturate CPU cores (mitigated by strict qubit/shot limits and rate limiting).

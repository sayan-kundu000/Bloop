# ADR-028: Quantum Circuit & Noise Laboratory, Experiments & Visualization

## Status
Accepted

## Context
Bloop's Quantum Intelligence platform has established foundational quantum computing capabilities (Prompt 22), text style intelligence (Prompt 23), affective emotion analysis (Prompt 24), and semantic similarity estimation (Prompt 25). 

Prompt 26 demands a dedicated **Quantum Circuit & Noise Laboratory**: an isolated experimental, benchmarking, and educational environment for:
1. Constructing bounded quantum circuits with an approved gate whitelist.
2. Simulating circuits on ideal (noise-free) backends.
3. Applying physically grounded decoherence noise models (depolarizing, bit-flip, phase-flip, bit-phase-flip, thermal relaxation with $T_2 \le 2T_1$, and readout error).
4. Performing side-by-side comparative experiments calculating Total Variation Distance (TVD) and Bhattacharyya Classical Fidelity.
5. Executing bounded parameter robustness sweeps to measure fidelity decay and target-state survival probabilities.
6. Ensuring 100% decoupling from core production Text-to-Speech (TTS) operations.

## Decision

### 1. Isolated Laboratory Architecture
We implement the laboratory under `backend/app/quantum/laboratory/`:
- `circuits/`: Safe declarative builder, bounds validator, and deterministic template catalog (`bell_state`, `ghz_state`, `hadamard_superposition`, `rotation_experiment`, `entanglement_experiment`).
- `noise/`: Parameter validator and factory for Qiskit Aer `NoiseModel` channels, with preset profiles (`IDEAL`, `LOW_NOISE`, `MEDIUM_NOISE`, `HIGH_NOISE`).
- `execution/`: Thread-isolated ideal and noisy AerSimulator execution engines with wall-clock timeout protection.
- `analysis/`: Measurement probability normalizer, Shannon entropy ($H = -\sum p \log_2 p$), dominant state detector, Total Variation Distance ($\text{TVD} = \frac{1}{2}\sum |p - q|$), Bhattacharyya Classical Fidelity ($F = \sum \sqrt{pq}$), and noise sweep robustness analyzer.
- `visualization/`: ASCII wire diagram generator, OpenQASM 2.0 exporter, and JSON-ready distribution and sweep chart formatters.
- `service.py`: `QuantumLaboratoryService` orchestrator managing Modes A, B, C, and D, and logging experiments to `QuantumExperimentRepository` isolated by `user_id`.

### 2. Four Operational Modes
- **Mode A (Ideal Simulation)**: Circuit $\to$ Ideal Simulator $\to$ Counts, Probabilities, Shannon Entropy, Statevector ($N \le 6$).
- **Mode B (Noisy Simulation)**: Circuit $\to$ Noise Model $\to$ Noisy Simulator $\to$ Measured Distributions.
- **Mode C (Comparative Experiment)**: Circuit $\to$ Simultaneous Ideal and Noisy Runs $\to$ TVD, Bhattacharyya Fidelity, State-by-State Divergence Table.
- **Mode D (Robustness Experiment)**: Circuit $\to$ Parameterized Noise Sweep ($\le 10$ steps, $\le 5$ repeats) $\to$ Fidelity Decay Curve, Mean/Std TVD, Latency.

### 3. Approved Gate Whitelist & Security Invariants
- Single-qubit: `H`, `X`, `Y`, `Z`, `S`, `T`
- Parameterized rotations: `RX`, `RY`, `RZ`
- Two-qubit entanglers: `CX`, `CZ`, `SWAP`
- Strict security: No `eval()`, `exec()`, or dynamic imports. Parameter validation rejects non-finite angles. Target and control qubit indices are strictly clamped within register bounds ($0 \le q < N$).

### 4. Rigorous Distinction Between State Fidelity and Classical Distribution Similarity
We enforce clear separation between:
- **Quantum State Fidelity**: $|\langle\psi|\phi\rangle|^2$ on complex Hilbert statevectors.
- **Measurement Distribution Similarity**: Classical overlap $F(P, Q) = \sum \sqrt{P(x) Q(x)}$ (Bhattacharyya coefficient) in the computational basis.
Measurement overlap does not capture off-diagonal quantum coherences or relative phases; this limitation is explicitly documented in backend methodology notes and frontend callouts.

### 5. Simulator-First & Scientific Integrity
- All simulations run locally on classical CPU backends via Qiskit AerSimulator.
- No cloud quantum hardware accounts (IBM Quantum, AWS Braket) or API keys are required.
- No false claims of "quantum supremacy" or "quantum advantage" are permitted; the system reports purely empirical metrics ($\text{TVD}$, classical fidelity, error rates, latencies).

## Consequences

### Positive
- Researchers and developers can study NISQ noise behavior, gate errors, and decoherence interactively.
- The laboratory is 100% decoupled: an error or disabling quantum intelligence never impacts core TTS.
- All experiment runs are persisted to PostgreSQL with tenant isolation by `user_id`.
- Complete test suite passes with 126/126 quantum tests and 12/12 core regression tests.

### Negative
- Qiskit Aer simulation is classical; large qubit counts ($N > 8$) or deep circuits remain bounded by classical memory and CPU limits.

## Implemented vs. Experimental vs. Future Research

| Subsystem | Implemented | Experimental | Future Research |
| :--- | :---: | :---: | :---: |
| Qiskit Aer Ideal Simulator | **Yes** | — | — |
| Depolarizing / Bit-Flip / Phase-Flip Noise | **Yes** | — | — |
| Thermal Relaxation ($T_1, T_2$) Decoherence | **Yes** | — | — |
| Readout Error Confusion Modeling | **Yes** | — | — |
| Total Variation Distance & Classical Fidelity | **Yes** | — | — |
| Bounded Parameter Robustness Sweeps | **Yes** | — | — |
| Cloud QPU Hardware Adapters (IBM / Braket) | — | — | Planned (Prompt 27+) |

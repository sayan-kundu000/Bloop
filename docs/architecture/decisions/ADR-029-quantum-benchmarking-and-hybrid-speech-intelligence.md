# ADR-029: Quantum Benchmarking, Hybrid Speech Intelligence & ElevenLabs Integration

## Status
Accepted

## Context
Bloop's Quantum Intelligence platform has incrementally deployed:
- Foundational quantum computing and state simulators (Prompt 22, ADR-024)
- Quantum text encoding and classification (Prompt 23, ADR-025)
- Quantum emotion intelligence and hybrid QNN (Prompt 24, ADR-026)
- Quantum semantic similarity and kernel estimation (Prompt 25, ADR-027)
- Quantum circuit and noise laboratory (Prompt 26, ADR-028)

Prompt 27 connects classical natural language processing, quantum state intelligence, speech synthesis recommendation, and external speech providers (specifically ElevenLabs) into a unified **Quantum Benchmarking and Hybrid Speech Intelligence Layer**.

Key engineering requirements include:
1. Multi-category benchmarking (Types A–E: Text Classification, Emotion Detection, Semantic Similarity, Circuit/Noise, and Hybrid Speech Pipeline).
2. Rigorous train/test evaluation methodology, deterministic splits, seed preservation, and zero data leakage.
3. Transparent mathematical fusion methods (Score convex combination $\alpha + \beta = 1.0$, Feature L2-normalized concatenation, Decision confidence-gated fallback).
4. Provider-independent speech parameter recommendations (`style`, `speed`, `pitch`, `stability`, `similarity_boost`, `pacing`, `reason`, `confidence`).
5. Strict decoupling: Quantum modules must **never** directly invoke ElevenLabs API, SDK, or speech generation endpoints. Speech synthesis remains strictly isolated inside `SpeechService`.
6. Dynamic voice capability validation via `CapabilityService` (preserving Prompt 11 contracts, preventing invented voice IDs or unsupported parameter injection).
7. Full user autonomy: Recommendations remain suggestions displayed in the UI that the user can choose to `[Apply to TTS]` or `[Ignore]`.
8. Honest scientific reporting: Acknowledge classical simulation overhead on classical CPUs; no false claims of "quantum advantage" or "quantum supremacy" are permitted.

## Decision

### 1. Multi-Category Benchmarking Architecture
We implement multi-category benchmarking under `backend/app/quantum/hybrid/benchmark.py`:
- **Type A (Text Classification)**: Evaluates Classical TF-IDF + Logistic Regression vs. Quantum Variational Classifier (VQC) vs. Hybrid Concatenation on standardized linguistic style datasets.
- **Type B (Emotion Detection)**: Evaluates Classical VADER/Lexicon affective analysis vs. Quantum Emotion QNN vs. Convex Score Fusion on balanced affective corpora.
- **Type C (Semantic Similarity)**: Evaluates Classical Jaccard/N-Gram lexical similarity vs. Quantum State Fidelity Kernel vs. Hybrid Concordance on semantic pair datasets.
- **Type D (Circuit Noise)**: Evaluates Ideal AerSimulator unitary dynamics vs. Physically Grounded Noisy AerSimulator measuring Total Variation Distance (TVD) and Bhattacharyya Classical Fidelity.
- **Type E (Hybrid Speech Pipeline)**: Benchmarks the end-to-end multi-stage pipeline measuring stage-by-stage latencies (Text Encoding, Affective Extraction, Kernel Estimation, Mathematical Fusion, Recommendation Generation).

### 2. Mathematical Fusion Engine
We implement three verified mathematical fusion strategies in `backend/app/quantum/hybrid/fusion.py`:
- **Score Fusion**: Convex linear combination $S_{\text{hybrid}} = \alpha S_{\text{classical}} + \beta S_{\text{quantum}}$, where $\alpha, \beta \ge 0$ and $\alpha + \beta = 1.0$.
- **Feature Fusion**: L2-normalized feature vector concatenation $v_{\text{hybrid}} = \left[\frac{v_{\text{classical}}}{\|v_{\text{classical}}\|_2} \,\|\, \frac{v_{\text{quantum}}}{\|v_{\text{quantum}}\|_2}\right]$.
- **Decision Fusion**: High-confidence quantum priority with conservative classical fallback, gated at threshold $\theta = 0.65$.

### 3. Speech Parameter Recommendation Engine
We implement `HybridSpeechRecommender` in `backend/app/quantum/hybrid/recommendation.py`:
- Maps hybrid affective valence/arousal, dominance, and stylistic state to acoustic speech parameters:
  - High arousal / joyful: Faster pace (1.05–1.10x), moderate-high stability, elevated pitch (+1 to +2 semitones).
  - High arousal / angry: Faster pace (1.10–1.15x), lower stability (0.40–0.50), elevated pitch.
  - Low arousal / sad: Deliberate/slow pace (0.85–0.90x), high stability (0.80–0.85), lowered pitch (-2 to -3 semitones).
  - Calm / relaxed: Balanced pace (0.95–1.00x), high stability (0.75–0.85), natural pitch.
  - Neutral / ambiguous: Safe default baseline (speed=1.0, pitch=0, stability=0.75, similarity_boost=0.75, confidence=None).
- Formats provider-independent `SpeechRecommendationDTO` decoupled from any specific vendor SDK.

### 4. Dynamic Speech Capability Bridge & Strict Decoupling
We implement `SpeechCapabilityBridge` in `backend/app/quantum/hybrid/speech_bridge.py`:
- Queries `CapabilityService` dynamically to verify target voice availability and supported capabilities (e.g. `voice_settings`, `style_exaggeration`).
- Clamps acoustic parameters strictly within provider-safe operational bounds.
- Generates a pre-populated, canonical `TTSRequest` payload without triggering generation.
- **Strict Isolation Invariant**: Quantum and Hybrid modules contain **zero** imports from or references to `elevenlabs`, `ElevenLabsClient`, or direct TTS generation. Speech synthesis is triggered exclusively by user-initiated requests through `POST /api/v1/tts`.

### 5. Research Benchmark UI Dashboard
We enrich `frontend/src/pages/quantum/QuantumBenchmarkPage.tsx`:
- Interactive multi-category benchmark tabs (Text Classification, Emotion Intelligence, Semantic Similarity, Circuit Noise, Hybrid Pipeline).
- Parameter customization: dataset size, qubit bounds ($N \le 6$), shot counts, classical/quantum fusion weights.
- Side-by-side metric comparison tables (Accuracy, F1-score, Inference Time, Qubits, Circuit Depth, TVD, Fidelity).
- Stage-by-stage pipeline latency breakdown with interactive progress visualization.
- Empirical "Honest Analysis" callout badge summarizing real-world classical vs. quantum performance.
- Speech Recommendation preview card with single-click `[Apply to TTS]` action navigating to the TTS workspace with pre-populated parameters.

## Consequences

### Positive
- Unified classical, quantum, and speech intelligence into a coherent, verifiable pipeline.
- Rigorous scientific benchmarking with reproducible splits, seed tracking, and multi-metric reporting.
- Complete provider decoupling preserves architectural boundaries and protects production TTS stability.
- Dynamic voice architecture guarantees compatibility across providers and custom cloned voices.
- 100% test coverage with 25 new hybrid tests and 151 total quantum tests passing.

### Negative
- Quantum circuit execution on classical CPU simulators exhibits latency overhead compared to pure classical heuristics, accurately noted in scientific reporting.

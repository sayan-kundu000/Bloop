# Bloop REST API — Quantum Intelligence Domain Specification

## 1. Overview & Decoupled Fault Isolation Architecture

The **Quantum Intelligence Domain** provides quantum-enhanced neural text classification, parameter-shift emotion modulation, and parameterizable Qiskit/PennyLane quantum circuit simulation.

### Decoupling & Fault Isolation Architecture
1. **Zero Impact on Audio Synthesis:** The quantum subsystem is strictly decoupled from the core text-to-speech engine. If quantum analysis encounters a failure, timeout, or is explicitly disabled in configuration (`QUANTUM_ENABLED=false`), the TTS engine smoothly falls back to classical heuristic acoustic parameters.
2. **Predictable 503 Service Unavailable:** Calling quantum endpoints when the subsystem is disabled returns an immediate HTTP 503 error with code `QUANTUM_DISABLED`, providing clear feedback to the UI without throwing unhandled exceptions.

---

## 2. Endpoints

### 2.1 Quantum Text Intelligence & Classification

Processes input text through a decoupled hybrid quantum NLP pipeline: text validation, TF-IDF feature extraction, TruncatedSVD dimensionality reduction, $[0, \pi]$ angle encoding, parameterized quantum circuit execution (Qiskit Aer or PennyLane), and dual evaluation comparing the hybrid quantum classifier against a classical baseline.

- **Method:** `POST`
- **Path:** `/api/v1/quantum/text`
- **Access:** Protected (`Authorization: Bearer <token>`)
- **Rate Limit:** 15 requests per minute (`RATE_LIMIT_PER_MINUTE_QUANTUM`)
- **Success Status:** `200 OK`

#### Request Payload (`QuantumTextRequest`)
```json
{
  "text": "The quantum superposition state reveals intricate acoustic resonance.",
  "task": "classification",
  "model": "hybrid_quantum_classifier",
  "framework": "qiskit",
  "num_qubits": 4,
  "shots": 1024,
  "circuit_depth": 2
}
```

*Note: Backward-compatible requests providing only `{"text": "...", "num_qubits": 4, "shots": 512}` are fully supported.*

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "input_text": "The quantum superposition state reveals intricate acoustic resonance.",
    "tokens": ["quantum", "superposition", "state", "reveals", "intricate", "acoustic", "resonance"],
    "classical_features": [0.428, 0.781, 0.312, 0.519],
    "quantum_state_vector": null,
    "quantum_probabilities": {
      "0000": 0.312,
      "0001": 0.245,
      "1111": 0.443
    },
    "predicted_style": "technical",
    "confidence": 0.85,
    "classical_baseline_prediction": "technical",
    "classical_confidence": 0.88,
    "circuit_depth": 2,
    "num_qubits": 4,
    "execution_time_ms": 42.5,
    "task": "classification",
    "model": "hybrid_quantum_classifier",
    "prediction": {
      "quantum_predicted_class": "technical",
      "classical_predicted_class": "technical",
      "agreement": true
    },
    "metrics": {
      "accuracy": 0.833,
      "precision": 0.850,
      "recall": 0.833,
      "f1_score": 0.825,
      "training_time_seconds": 0.045,
      "prediction_time_seconds": 0.012
    },
    "quantum": {
      "framework": "qiskit",
      "circuit_depth": 2,
      "num_qubits": 4,
      "shots": 1024,
      "encoding": "angle",
      "probabilities": {
        "0000": 0.312,
        "0001": 0.245,
        "1111": 0.443
      }
    },
    "pipeline_steps": [
      "text_validation",
      "classical_tfidf_extraction",
      "truncated_svd_reduction",
      "angle_normalization",
      "quantum_feature_encoding",
      "parameterized_circuit_execution",
      "hybrid_classification",
      "classical_baseline_evaluation"
    ],
    "classical_baseline": {
      "model": "logistic_regression",
      "predicted_class": "technical",
      "accuracy": 0.833,
      "precision": 0.850,
      "recall": 0.833,
      "f1_score": 0.825
    }
  },
  "message": "Quantum text classification complete."
}
```

#### Error Response when Disabled (`503 Service Unavailable`)
```json
{
  "success": false,
  "error": {
    "code": "QUANTUM_DISABLED",
    "message": "Quantum subsystem is disabled in the active configuration profile.",
    "details": {
      "subsystem": "quantum",
      "enabled": false
    }
  }
}
```

---

### 2.2 Quantum Emotion Intelligence & Speech Recommendation

Executes a trainable Hybrid Quantum Neural Network (QNN) to analyze affective states (`joy`, `sadness`, `anger`, `neutral`) from text and generates optional speech synthesis recommendations with complete user autonomy.

- **Method:** `POST`
- **Path:** `/api/v1/quantum/emotion`
- **Access:** Protected (`Authorization: Bearer <token>`)
- **Rate Limit:** 15 requests per minute (`RATE_LIMIT_PER_MINUTE_QUANTUM`)
- **Success Status:** `200 OK`

#### Request Payload (`QuantumEmotionRequest`)
```json
{
  "text": "I am thrilled and absolutely delighted with this amazing breakthrough!",
  "shots": 1024,
  "num_qubits": 4,
  "circuit_depth": 4,
  "framework": "pennylane",
  "include_recommendation": true
}
```

*Note: Backward-compatible requests providing only `{"text": "...", "shots": 1024}` are fully supported.*

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "input_text": "I am thrilled and absolutely delighted with this amazing breakthrough!",
    "detected_emotion": "joy",
    "emotion_scores": {
      "joy": 0.765,
      "neutral": 0.125,
      "sadness": 0.055,
      "anger": 0.055
    },
    "quantum_probabilities": {
      "|joy>": 0.765,
      "|neutral>": 0.125,
      "|sadness>": 0.055,
      "|anger>": 0.055
    },
    "hybrid_qnn_confidence": 0.765,
    "classical_baseline_emotion": "joy",
    "classical_confidence": 0.812,
    "entanglement_entropy": 1.142,
    "circuit_depth": 10,
    "num_qubits": 4,
    "execution_time_ms": 38.5,
    "speech_recommendation": {
      "style": "expressive",
      "speed": 1.08,
      "pitch": 1.05,
      "stability": 0.50,
      "similarity_boost": 0.80,
      "pacing": "dynamic",
      "reason": "The analyzed text exhibits joyful affect; an expressive, slightly elevated tempo is recommended.",
      "confidence": 0.765,
      "applied": false
    },
    "metrics": {
      "accuracy": 0.900,
      "precision": 0.912,
      "recall": 0.900,
      "f1_score": 0.898,
      "training_time_seconds": 0.062,
      "inference_time_seconds": 0.015
    },
    "classical_baseline": {
      "model": "logistic_regression",
      "accuracy": 0.900,
      "precision": 0.912,
      "recall": 0.900,
      "f1_score": 0.898
    },
    "quantum": {
      "framework": "pennylane",
      "circuit_depth": 10,
      "num_qubits": 4,
      "shots": 1024,
      "entanglement_entropy": 1.142
    },
    "pipeline_steps": [
      "text_validation",
      "affective_feature_extraction",
      "truncated_svd_reduction",
      "angle_normalization",
      "hybrid_qnn_variational_circuit",
      "quantum_measurement_pauliz",
      "classical_decision_head",
      "speech_recommendation"
    ]
  },
  "message": "Quantum emotion analysis complete."
}
```

#### Error Response when Disabled (`503 Service Unavailable`)
```json
{
  "success": false,
  "error": {
    "code": "QUANTUM_DISABLED",
    "message": "Quantum subsystem is disabled in the active configuration profile.",
    "details": {
      "subsystem": "quantum",
      "enabled": false
    }
  }
}
```

---

### 2.3 Parameterized Quantum Circuit Simulation

Simulates an arbitrary or predefined quantum circuit, returning statevector probabilities and measurement counts.

- **Method:** `POST`
- **Path:** `/api/v1/quantum/circuit/simulate`
- **Access:** Public
- **Success Status:** `200 OK`

#### Request Payload (`QuantumCircuitSimulationRequest`)
```json
{
  "circuit_type": "bell_state",
  "num_qubits": 2,
  "shots": 1024
}
```

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "circuit_type": "bell_state",
    "measurement_counts": {
      "00": 519,
      "11": 505
    },
    "statevector": [0.7071, 0, 0, 0.7071],
    "entropy": 0.9998,
    "execution_time_ms": 18.5
  },
  "message": "Quantum circuit simulation completed."
}
```

---

### 2.4 Quantum Semantic Intelligence, Similarity & Classical Baseline (Prompt 25)

Computes text-to-text semantic similarity by comparing a transparent classical TF-IDF cosine similarity baseline against quantum kernel state transition fidelity ($K(A, B) = |\langle\phi(A)|\psi(B)\rangle|^2$).

#### 2.4.1 Pairwise Semantic Similarity
- **Method:** `POST`
- **Path:** `/api/v1/quantum/semantic`
- **Access:** Authenticated (`Bearer <JWT>`)
- **Success Status:** `200 OK`

##### Request Payload (`QuantumSemanticRequest`)
```json
{
  "text_a": "Artificial intelligence converts written text into natural human speech.",
  "text_b": "AI models synthesize voice audio from text input prompts.",
  "method": "hybrid",
  "framework": "qiskit",
  "num_qubits": 4,
  "shots": 1024
}
```

##### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "text_a": "Artificial intelligence converts written text into natural human speech.",
    "text_b": "AI models synthesize voice audio from text input prompts.",
    "quantum_kernel_similarity": 0.8452,
    "classical_cosine_similarity": 0.7821,
    "similarity_verdict": "Strongly Similar",
    "divergence": 0.0631,
    "num_qubits": 4,
    "circuit_depth": 14,
    "execution_time_ms": 28.5,
    "method": "hybrid",
    "similarity_score": 0.8137,
    "classical_similarity": 0.7821,
    "quantum_similarity": 0.8452,
    "hybrid_similarity": 0.8137,
    "semantic_distance": 0.1863,
    "feature_dimension": 64,
    "reduced_dimension": 4,
    "representation_method": "TF-IDF (Sublinear Term Frequency-Inverse Document Frequency)",
    "reduction_method": "TruncatedSVD / Deterministic Band Pooling",
    "encoding_method": "Continuous Angle Encoding (Ry)",
    "quantum_framework": "qiskit",
    "quantum_backend": "qiskit_aer_simulator",
    "shots": 1024,
    "pipeline_steps": [
      "1. Text Validation & Preprocessing",
      "2. Classical TF-IDF Feature Extraction",
      "3. Classical Cosine Similarity Baseline",
      "4. Dimensionality Reduction (TruncatedSVD / Pooling)",
      "5. Angle Normalization ([0, pi])",
      "6. Quantum Kernel Fidelity Simulation (Qiskit)",
      "7. Similarity Resolution & Neutral Interpretation"
    ]
  },
  "message": "Quantum semantic similarity computed."
}
```

#### 2.4.2 Pairwise Similarity Matrix
- **Method:** `POST`
- **Path:** `/api/v1/quantum/semantic/matrix`
- **Access:** Authenticated (`Bearer <JWT>`)
- **Success Status:** `200 OK`

##### Request Payload (`SemanticMatrixRequest`)
```json
{
  "texts": [
    "Speech synthesis audio platform.",
    "Voice generation text engine.",
    "Quantum computing simulation."
  ],
  "method": "hybrid",
  "num_qubits": 4
}
```

#### 2.4.3 Empirical Benchmark
- **Method:** `POST`
- **Path:** `/api/v1/quantum/semantic/benchmark`
- **Access:** Authenticated (`Bearer <JWT>`)
- **Success Status:** `200 OK`

##### Request Payload (`SemanticBenchmarkRequest`)
```json
{
  "num_qubits": 4,
  "shots": 1024,
  "framework": "qiskit"
}
```

##### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "dataset_name": "BSEB-v1 (Bloop Semantic Evaluation Benchmark)",
    "sample_count": 12,
    "classical_metrics": {
      "mae": 0.0821,
      "rmse": 0.1042,
      "pearson_correlation": 0.9412,
      "spearman_correlation": 0.9231,
      "average_latency_ms": 1.25
    },
    "quantum_metrics": {
      "mae": 0.0915,
      "rmse": 0.1180,
      "pearson_correlation": 0.9284,
      "spearman_correlation": 0.9102,
      "average_latency_ms": 12.45
    },
    "correlation_pearson": 0.9284,
    "correlation_spearman": 0.9102,
    "mae": 0.0915,
    "rmse": 0.1180,
    "honest_analysis": "Classical baseline (TF-IDF + Cosine) achieved MAE=0.0821 and Pearson r=0.9412 with lower latency. Quantum kernel state fidelity exhibited competitive correlation without demonstrating quantum supremacy on classical simulation hardware.",
    "execution_time_ms": 164.2
  },
  "message": "Semantic benchmark evaluation completed."
}
```

---

### 2.5 Quantum Circuit & Noise Laboratory (Prompt 26)

Provides interactive circuit construction, simulation under ideal dynamics or controlled noise channels, side-by-side comparative distribution experiments, and parameter robustness sweeps.

#### 2.5.1 Single Circuit Simulation (Mode A / Mode B)
- **Method:** `POST`
- **Path:** `/api/v1/quantum/circuit`
- **Access:** Authenticated (`Bearer <JWT>`)
- **Rate Limit:** 15 req/min
- **Success Status:** `200 OK`

##### Request Payload (`QuantumCircuitRequest`)
```json
{
  "num_qubits": 2,
  "gates": [
    { "gate": "h", "target": 0 },
    { "gate": "cx", "control": 0, "target": 1 }
  ],
  "shots": 1024,
  "noise_profile": "medium_noise"
}
```

##### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "num_qubits": 2,
    "circuit_depth": 2,
    "total_gates": 2,
    "counts": { "00": 482, "11": 490, "01": 28, "10": 24 },
    "probabilities": { "00": 0.4707, "11": 0.4785, "01": 0.0273, "10": 0.0234 },
    "state_vector": null,
    "qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\n",
    "circuit_diagram_ascii": "     ┌───┐     ┌─┐   \nq_0: ┤ H ├──■──┤M├───\n     └───┘┌─┴─┐└╥┘┌─┐\nq_1: ─────┤ X ├─╫─┤M├\n          └───┘ ║ └╥┘\nc: 2/═══════════╩══╩═\n                0  1 ",
    "is_noisy_simulation": true,
    "execution_time_ms": 14.8,
    "entropy": 1.2845,
    "dominant_state": "11",
    "noise_model": "profile:medium_noise",
    "framework": "qiskit",
    "backend": "aer_simulator"
  },
  "message": "Quantum circuit simulated successfully."
}
```

#### 2.5.2 Ideal vs Noisy Comparative Experiment (Mode C)
- **Method:** `POST`
- **Path:** `/api/v1/quantum/circuit/compare`
- **Access:** Authenticated (`Bearer <JWT>`)
- **Success Status:** `200 OK`

##### Request Payload (`CircuitComparisonRequest`)
```json
{
  "num_qubits": 2,
  "preset": "bell_state",
  "shots": 1024,
  "noise_profile": "medium_noise"
}
```

##### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "num_qubits": 2,
    "circuit_depth": 2,
    "total_gates": 2,
    "ideal_counts": { "00": 512, "11": 512 },
    "noisy_counts": { "00": 485, "11": 487, "01": 27, "10": 25 },
    "ideal_probabilities": { "00": 0.5, "11": 0.5 },
    "noisy_probabilities": { "00": 0.4736, "11": 0.4756, "01": 0.0264, "10": 0.0244 },
    "total_variation_distance": 0.0508,
    "classical_fidelity": 0.9742,
    "ideal_entropy": 1.0,
    "noisy_entropy": 1.2915,
    "max_divergence": 0.0264,
    "dominant_ideal_state": "00",
    "dominant_noisy_state": "11",
    "states_comparison": [
      {
        "state": "00",
        "ideal_count": 512,
        "noisy_count": 485,
        "ideal_probability": 0.5,
        "noisy_probability": 0.4736,
        "divergence": 0.0264
      },
      {
        "state": "11",
        "ideal_count": 512,
        "noisy_count": 487,
        "ideal_probability": 0.5,
        "noisy_probability": 0.4756,
        "divergence": 0.0244
      }
    ],
    "circuit_diagram_ascii": "...",
    "noise_model": "medium_noise",
    "execution_time_ms": 22.4
  },
  "message": "Circuit comparison completed successfully."
}
```

#### 2.5.3 Noise Parameter Robustness Sweep (Mode D)
- **Method:** `POST`
- **Path:** `/api/v1/quantum/circuit/robustness`
- **Access:** Authenticated (`Bearer <JWT>`)
- **Success Status:** `200 OK`

##### Request Payload (`CircuitRobustnessRequest`)
```json
{
  "num_qubits": 2,
  "preset": "bell_state",
  "noise_model": "depolarizing",
  "sweep": {
    "parameter": "probability",
    "start": 0.0,
    "stop": 0.06,
    "step": 0.02
  },
  "shots": 1024,
  "repeats_per_point": 1
}
```

##### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "sweep_parameter": "probability",
    "points": [
      { "parameter_value": 0.0, "mean_fidelity": 1.0, "std_fidelity": 0.0, "mean_tvd": 0.0, "std_tvd": 0.0, "success_probability": 0.505, "execution_time_ms": 4.2, "repetition_count": 1 },
      { "parameter_value": 0.02, "mean_fidelity": 0.978, "std_fidelity": 0.0, "mean_tvd": 0.038, "std_tvd": 0.0, "success_probability": 0.485, "execution_time_ms": 5.1, "repetition_count": 1 },
      { "parameter_value": 0.04, "mean_fidelity": 0.952, "std_fidelity": 0.0, "mean_tvd": 0.076, "std_tvd": 0.0, "success_probability": 0.468, "execution_time_ms": 5.3, "repetition_count": 1 },
      { "parameter_value": 0.06, "mean_fidelity": 0.924, "std_fidelity": 0.0, "mean_tvd": 0.114, "std_tvd": 0.0, "success_probability": 0.449, "execution_time_ms": 5.4, "repetition_count": 1 }
    ],
    "target_state": "00",
    "baseline_ideal_state": "00",
    "circuit_depth": 2,
    "total_gates": 2,
    "total_runs": 4,
    "total_execution_time_ms": 24.8,
    "summary": "Sweep across 4 levels of depolarizing noise (0.0 to 0.06) resulted in fidelity change of 1.0000 -> 0.9240 (Δ=-0.0760) for target state |00⟩."
  },
  "message": "Circuit robustness experiment completed successfully."
}
```

#### 2.5.4 Catalogs & Specifications
- `GET /api/v1/quantum/circuit/templates`: Returns deterministic templates.
- `GET /api/v1/quantum/circuit/noise-profiles`: Returns preset noise profiles.
- `GET /api/v1/quantum/circuit/gates`: Returns approved gate whitelist specifications.

---

### 2.6 Quantum Benchmarking & Hybrid Speech Intelligence (Prompt 27)

#### 2.6.1 List Benchmark Categories
Returns all supported empirical benchmark categories, their descriptions, evaluation metrics, and resource parameters.

- **Method:** `GET`
- **Path:** `/api/v1/quantum/benchmark/categories`
- **Access:** Public or Authenticated
- **Success Status:** `200 OK`

##### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": [
    {
      "category": "text_classification",
      "name": "Text Style Classification (Type A)",
      "description": "Evaluates Classical TF-IDF + Logistic Regression vs. Quantum VQC vs. Hybrid Concatenation.",
      "classical_baseline": "TF-IDF + Logistic Regression",
      "quantum_model": "Variational Quantum Classifier (VQC)",
      "hybrid_model": "Feature Concatenation",
      "supported_metrics": ["accuracy", "f1_score", "inference_time_seconds"]
    },
    {
      "category": "emotion_detection",
      "name": "Affective Emotion Detection (Type B)",
      "description": "Evaluates Classical Lexicon/VADER vs. PennyLane Emotion QNN vs. Score Convex Fusion.",
      "classical_baseline": "Rule-Based Affective Lexicon",
      "quantum_model": "PennyLane Hybrid QNN",
      "hybrid_model": "Convex Score Fusion",
      "supported_metrics": ["accuracy", "f1_score", "inference_time_seconds"]
    },
    {
      "category": "semantic_similarity",
      "name": "Semantic Similarity & Kernel (Type C)",
      "description": "Evaluates Classical Jaccard/N-Gram vs. Quantum State Fidelity Kernel vs. Hybrid Concordance.",
      "classical_baseline": "Jaccard / Character N-Gram Overlap",
      "quantum_model": "Quantum State Transition Fidelity Kernel",
      "hybrid_model": "Concordance Average",
      "supported_metrics": ["pearson_correlation", "spearman_correlation", "mae", "rmse"]
    },
    {
      "category": "circuit_noise",
      "name": "Quantum Circuit & Noise Analysis (Type D)",
      "description": "Evaluates Ideal Unitary AerSimulator vs. Physically Grounded Noisy AerSimulator.",
      "classical_baseline": "Ideal AerSimulator (Unitary)",
      "quantum_model": "Noisy AerSimulator (Kraus Channels)",
      "hybrid_model": null,
      "supported_metrics": ["tvd", "fidelity", "circuit_depth"]
    },
    {
      "category": "hybrid_speech_pipeline",
      "name": "End-to-End Hybrid Speech Pipeline (Type E)",
      "description": "Benchmarks the full multi-stage pipeline measuring stage-by-stage latencies.",
      "classical_baseline": "Direct Heuristic Speech Modulation",
      "quantum_model": "Quantum Emotion & Kernel Modulation",
      "hybrid_model": "Fused Multi-Stage Speech Pipeline",
      "supported_metrics": ["total_pipeline_latency_ms", "accuracy", "f1_score"]
    }
  ],
  "message": "Benchmark categories retrieved successfully."
}
```

#### 2.6.2 Execute Multi-Category Benchmark
Executes reproducible, zero-data-leakage benchmark evaluating classical, quantum, and hybrid models side-by-side.

- **Method:** `POST`
- **Path:** `/api/v1/quantum/benchmark`
- **Access:** Authenticated (`Bearer <JWT>`)
- **Success Status:** `200 OK`

##### Request Payload (`BenchmarkRequest`)
```json
{
  "category": "text_classification",
  "dataset_size": 20,
  "test_split_ratio": 0.3,
  "random_seed": 42,
  "num_qubits": 4,
  "shots": 1024,
  "classical_weight": 0.5,
  "quantum_weight": 0.5
}
```

##### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "category": "text_classification",
    "dataset": {
      "dataset_name": "Standard Linguistic Style Corpus",
      "sample_count": 20,
      "train_count": 14,
      "test_count": 6,
      "random_seed": 42
    },
    "classical_model": "TF-IDF + Logistic Regression",
    "quantum_model": "Variational Quantum Classifier (VQC)",
    "hybrid_model": "Feature Concatenation",
    "classical_metrics": {
      "accuracy": 0.8333,
      "f1_score": 0.8333,
      "inference_time_seconds": 0.0032
    },
    "quantum_metrics": {
      "accuracy": 0.6667,
      "f1_score": 0.6667,
      "inference_time_seconds": 0.4125,
      "qubits": 4,
      "shots": 1024,
      "circuit_depth": 2
    },
    "hybrid_metrics": {
      "accuracy": 0.8333,
      "f1_score": 0.8333,
      "inference_time_seconds": 0.4162
    },
    "honest_analysis": "On a dataset of 20 samples, Classical achieved 83.3% accuracy in 3.2ms while Quantum achieved 66.7% accuracy in 412.5ms. Classical CPU execution demonstrates a 128.9x speedup over simulated quantum circuits.",
    "quantum_advantage_detected": false
  },
  "message": "Benchmark completed successfully."
}
```

#### 2.6.3 Hybrid Text & Emotion Analysis
Performs unified classical, quantum, and fused affective intelligence analysis on input text.

- **Method:** `POST`
- **Path:** `/api/v1/quantum/hybrid/analyze`
- **Access:** Authenticated (`Bearer <JWT>`)
- **Success Status:** `200 OK`

##### Request Payload (`HybridAnalysisRequest`)
```json
{
  "text": "The experimental results demonstrate remarkable quantum coherence across all test registers!",
  "num_qubits": 4,
  "shots": 1024,
  "fusion_method": "score_fusion",
  "classical_weight": 0.5,
  "quantum_weight": 0.5,
  "experiment_mode": "hybrid"
}
```

##### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "text": "The experimental results demonstrate remarkable quantum coherence across all test registers!",
    "classical": {
      "predicted_class": "joy",
      "confidence": 0.72,
      "probabilities": { "joy": 0.72, "neutral": 0.18, "sadness": 0.05, "anger": 0.05 },
      "valence": 0.65,
      "arousal": 0.55
    },
    "quantum": {
      "predicted_class": "joy",
      "confidence": 0.70,
      "probabilities": { "joy": 0.70, "neutral": 0.20, "sadness": 0.05, "anger": 0.05 },
      "qubits": 4,
      "shots": 1024,
      "circuit_depth": 3
    },
    "fused_prediction": "joy",
    "fused_confidence": 0.71,
    "fused_probabilities": { "joy": 0.71, "neutral": 0.19, "sadness": 0.05, "anger": 0.05 },
    "fusion_method": "score_fusion",
    "weights": { "classical": 0.5, "quantum": 0.5 },
    "pipeline_breakdown": {
      "text_encoding_ms": 2.1,
      "affective_extraction_ms": 1.8,
      "circuit_simulation_ms": 38.4,
      "mathematical_fusion_ms": 0.5,
      "recommendation_generation_ms": 0.2,
      "total_pipeline_ms": 43.0
    },
    "recommendation": {
      "speed": 1.08,
      "pitch": 1.5,
      "stability": 0.72,
      "similarity_boost": 0.75,
      "style": "joyful",
      "pacing": "brisk",
      "reason": "Elevated valence (0.65) and arousal (0.55) detected in text, warranting brisk pacing and bright pitch modulation.",
      "confidence": 0.71
    }
  },
  "message": "Hybrid analysis completed successfully."
}
```

#### 2.6.4 Speech Parameter Recommendation
Generates decoupled acoustic parameter recommendations based on text or hybrid analysis.

- **Method:** `POST`
- **Path:** `/api/v1/quantum/hybrid/recommend`
- **Access:** Authenticated (`Bearer <JWT>`)
- **Success Status:** `200 OK`

##### Request Payload (`SpeechRecommendationRequest`)
```json
{
  "text": "The dark clouds gathered as silence fell across the abandoned laboratory.",
  "target_voice_id": "21m00Tcm4TlvDq8ikWAM"
}
```

##### Success Response (`200 OK`)
```json
{
  "success": true,
  "data": {
    "speed": 0.88,
    "pitch": -2.0,
    "stability": 0.82,
    "similarity_boost": 0.75,
    "style": "somber",
    "pacing": "deliberate",
    "reason": "Lower valence (-0.52) and low arousal detected, mapped to deliberate pacing, stable delivery, and deeper pitch.",
    "confidence": 0.68
  },
  "message": "Speech recommendation generated successfully."
}
```



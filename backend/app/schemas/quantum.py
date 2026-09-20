from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator, field_validator


# 1. Quantum Text Intelligence Schemas
class QuantumTextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    task: Optional[str] = "classification"
    model: Optional[str] = "hybrid_quantum_classifier"
    framework: Optional[str] = "qiskit"
    circuit_depth: Optional[int] = Field(2, ge=1, le=6)
    category_target: Optional[str] = None  # e.g., "formal", "casual", "technical", "creative"
    num_qubits: int = Field(4, ge=2, le=8)
    shots: int = Field(1024, ge=100, le=4096)


class QuantumTextResponse(BaseModel):
    input_text: str
    tokens: List[str]
    classical_features: List[float]
    quantum_state_vector: Optional[List[float]] = None
    quantum_probabilities: Dict[str, float]
    predicted_style: str
    confidence: Optional[float] = 0.85
    classical_baseline_prediction: str
    classical_confidence: Optional[float] = 0.85
    circuit_depth: int
    num_qubits: int
    execution_time_ms: float

    # Prompt 23 Enrichments
    task: Optional[str] = "classification"
    model: Optional[str] = "hybrid_quantum_classifier"
    prediction: Optional[Any] = None
    metrics: Optional[Dict[str, Any]] = None
    quantum: Optional[Dict[str, Any]] = None
    pipeline_steps: Optional[List[str]] = None
    classical_baseline: Optional[Dict[str, Any]] = None


# 2. Quantum Emotion Intelligence Schemas
class QuantumEmotionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    shots: int = Field(1024, ge=100, le=4096)
    include_recommendation: Optional[bool] = True
    framework: Optional[str] = "pennylane"
    num_qubits: Optional[int] = Field(4, ge=2, le=8)
    circuit_depth: Optional[int] = Field(4, ge=1, le=8)


class QuantumEmotionResponse(BaseModel):
    input_text: str
    detected_emotion: str  # joy, sadness, anger, fear, neutral
    emotion_scores: Dict[str, float]
    quantum_probabilities: Dict[str, float]
    hybrid_qnn_confidence: Optional[float] = 0.85
    classical_baseline_emotion: str
    classical_confidence: Optional[float] = 0.85
    entanglement_entropy: float
    circuit_depth: int
    num_qubits: int
    execution_time_ms: float

    # Prompt 24 Enrichments
    speech_recommendation: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    classical_baseline: Optional[Dict[str, Any]] = None
    quantum: Optional[Dict[str, Any]] = None
    pipeline_steps: Optional[List[str]] = None


# 3. Quantum Semantic Intelligence Schemas
class QuantumSemanticRequest(BaseModel):
    text_a: str = Field(..., min_length=1, max_length=1000)
    text_b: str = Field(..., min_length=1, max_length=1000)
    num_qubits: int = Field(4, ge=2, le=8)
    method: Optional[str] = Field("hybrid", description="Analysis method: 'hybrid', 'classical', or 'quantum'")
    framework: Optional[str] = Field("qiskit", description="Quantum framework: 'qiskit' or 'pennylane'")
    shots: Optional[int] = Field(1024, ge=100, le=4096)

    @field_validator("text_a", "text_b")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text snippet cannot be empty or whitespace-only.")
        return v.strip()


class QuantumSemanticResponse(BaseModel):
    text_a: str
    text_b: str
    quantum_kernel_similarity: float  # Fidelity |<phi(x)|psi(y)>|^2 between [0, 1]
    classical_cosine_similarity: float
    similarity_verdict: str  # "Identical", "Strongly Similar", "Moderately Similar", "Dissimilar"
    divergence: float
    num_qubits: int
    circuit_depth: int
    execution_time_ms: float

    # Prompt 25 Enrichments
    method: Optional[str] = "hybrid"
    similarity_score: Optional[float] = None
    classical_similarity: Optional[float] = None
    quantum_similarity: Optional[float] = None
    hybrid_similarity: Optional[float] = None
    semantic_distance: Optional[float] = None
    feature_dimension: Optional[int] = None
    reduced_dimension: Optional[int] = None
    representation_method: Optional[str] = None
    reduction_method: Optional[str] = None
    encoding_method: Optional[str] = None
    quantum_framework: Optional[str] = None
    quantum_backend: Optional[str] = None
    shots: Optional[int] = None
    experiment_id: Optional[str] = None
    pipeline_steps: Optional[List[str]] = None
    details: Optional[Dict[str, Any]] = None



# 4. Quantum Circuit Lab Schemas
class GateOperation(BaseModel):
    gate: str  # h, x, y, z, rx, ry, rz, cx, cz, swap
    target: int
    control: Optional[int] = None
    parameter: Optional[float] = None  # angle in radians for rx, ry, rz


class QuantumCircuitRequest(BaseModel):
    num_qubits: int = Field(2, ge=1, le=8)
    qubits: Optional[int] = Field(None, ge=1, le=8)
    gates: List[GateOperation] = Field(default_factory=list)
    preset: Optional[str] = None  # e.g., "bell_state", "single_qubit_h", "single_qubit_x", "ghz_state"
    framework: Optional[str] = "qiskit"
    experiment_type: Optional[str] = "basic_circuit"
    parameters: Optional[Dict[str, Any]] = None
    shots: int = Field(1024, ge=100, le=8192)
    noise_level: float = Field(0.0, ge=0.0, le=0.5, description="Depolarizing noise probability (0.0 = ideal)")
    noise: Optional[Dict[str, Any]] = None
    noise_profile: Optional[str] = None
    seed: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def resolve_qubit_count(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "qubits" in data and "num_qubits" not in data:
                data["num_qubits"] = data["qubits"]
        return data


class QuantumCircuitResponse(BaseModel):
    num_qubits: int
    circuit_depth: int
    total_gates: int
    counts: Dict[str, int]
    probabilities: Dict[str, float]
    state_vector: Optional[List[str]] = None
    qasm: str
    circuit_diagram_ascii: str
    is_noisy_simulation: bool
    execution_time_ms: float
    entropy: Optional[float] = None
    dominant_state: Optional[str] = None
    noise_model: Optional[str] = None
    seed: Optional[int] = None
    framework: Optional[str] = "qiskit"
    backend: Optional[str] = "aer_simulator"


# 5. Quantum Benchmarking Schemas
class BenchmarkRequest(BaseModel):
    dataset_size: int = Field(40, ge=10, le=150)
    test_split: float = Field(0.25, ge=0.1, le=0.5)
    num_qubits: int = Field(4, ge=2, le=6)
    shots: int = Field(512, ge=100, le=2048)
    category: Optional[str] = Field("text_classification", description="Benchmark category")
    random_seed: Optional[int] = Field(42, description="Random seed for reproducibility")
    classical_weight: Optional[float] = Field(0.5, ge=0.0, le=1.0)
    quantum_weight: Optional[float] = Field(0.5, ge=0.0, le=1.0)


class MetricComparison(BaseModel):
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mae: Optional[float] = None
    rmse: Optional[float] = None
    correlation: Optional[float] = None
    training_time_seconds: Optional[float] = 0.0
    inference_time_seconds: float = 0.0
    qubits: Optional[int] = None
    shots: Optional[int] = None
    circuit_depth: Optional[int] = None
    tvd: Optional[float] = None
    fidelity: Optional[float] = None


class QuantumBenchmarkResponse(BaseModel):
    classical_model: str
    quantum_model: str
    classical_metrics: MetricComparison
    quantum_metrics: MetricComparison
    honest_analysis: str
    quantum_advantage_detected: bool
    summary: str
    category: Optional[str] = "text_classification"
    dataset: Optional[Dict[str, Any]] = None
    hybrid_model: Optional[str] = None
    hybrid_metrics: Optional[MetricComparison] = None
    resource_usage: Optional[Dict[str, Any]] = None
    pipeline_breakdown: Optional[Dict[str, float]] = None
    speech_recommendation: Optional[Dict[str, Any]] = None


# Re-export laboratory schemas
from backend.app.quantum.laboratory.schemas import (
    CircuitComparisonRequestSchema as CircuitComparisonRequest,
    CircuitComparisonResponseSchema as CircuitComparisonResponse,
    CircuitRobustnessRequestSchema as CircuitRobustnessRequest,
    CircuitRobustnessResponseSchema as CircuitRobustnessResponse,
    TemplateInfoSchema,
    NoiseProfileInfoSchema,
    NoiseModelConfigSchema,
    NoiseSweepConfigSchema,
)

# Re-export hybrid schemas
from backend.app.quantum.hybrid.schemas import (
    FusionConfigSchema,
    SpeechRecommendationSchema,
    HybridAnalysisRequestSchema,
    HybridAnalysisResponseSchema,
    SpeechRecommendationRequestSchema,
    MultiCategoryBenchmarkRequestSchema,
    BenchmarkCategoryInfoSchema,
    MultiCategoryBenchmarkResponseSchema,
)

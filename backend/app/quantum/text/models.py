"""
Bloop Quantum Text Domain Models
Defines immutable domain structures, enumerations, and evaluation contracts
for Quantum Text Intelligence.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ClassificationTask(str, Enum):
    CLASSIFICATION = "classification"
    STYLE_CLASSIFICATION = "style_classification"
    BINARY_CLASSIFICATION = "binary_classification"


class EncodingStrategy(str, Enum):
    ANGLE = "angle"
    AMPLITUDE = "amplitude"
    BASIS = "basis"


class ClassifierStrategy(str, Enum):
    HYBRID_QUANTUM_CLASSIFIER = "hybrid_quantum_classifier"
    VARIATIONAL_QUANTUM_CLASSIFIER = "variational_quantum_classifier"
    CLASSICAL_BASELINE = "classical_baseline"


class TextFramework(str, Enum):
    QISKIT = "qiskit"
    PENNYLANE = "pennylane"


@dataclass(frozen=True)
class ClassificationMetrics:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_time_seconds: float
    prediction_time_seconds: float
    quantum_execution_time_seconds: Optional[float] = None


@dataclass(frozen=True)
class PipelineExplanation:
    steps: List[str]
    input_chars: int
    extracted_features_count: int
    reduced_dimensions: int
    qubit_count: int
    encoding_type: str
    circuit_depth: int
    decision_mechanism: str


@dataclass
class TextClassificationResult:
    task: str
    model: str
    prediction: Any
    confidence: Optional[float]
    metrics: Optional[ClassificationMetrics]
    quantum_metadata: Dict[str, Any]
    classical_baseline_prediction: Optional[Any] = None
    classical_baseline_confidence: Optional[float] = None
    classical_baseline_metrics: Optional[ClassificationMetrics] = None
    pipeline_explanation: Optional[PipelineExplanation] = None
    tokens: List[str] = field(default_factory=list)
    classical_features: List[float] = field(default_factory=list)
    quantum_probabilities: Dict[str, float] = field(default_factory=dict)
    circuit_depth: int = 0
    num_qubits: int = 4
    execution_time_ms: float = 0.0

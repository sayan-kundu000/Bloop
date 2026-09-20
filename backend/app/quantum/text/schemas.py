"""
Bloop Quantum Text Intelligence API Schemas
Defines request and response validation contracts, supporting both
Prompt 23 rich research contracts and existing backwards-compatible attributes.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class QuantumTextExperimentRequest(BaseModel):
    """Input contract for Quantum Text Intelligence classification and evaluation."""

    text: str = Field(..., min_length=1, max_length=1000, description="Input text to preprocess, encode, and classify.")
    task: str = Field("classification", description="Task type (classification, style_classification, binary_classification).")
    model: str = Field("hybrid_quantum_classifier", description="Classifier strategy (hybrid_quantum_classifier, variational_quantum_classifier).")
    framework: str = Field("qiskit", description="Quantum simulation framework (qiskit or pennylane).")
    num_qubits: int = Field(4, ge=2, le=8, description="Target qubit register width.")
    shots: int = Field(1024, ge=100, le=4096, description="Measurement execution shot count.")
    circuit_depth: int = Field(2, ge=1, le=6, description="Variational layer depth.")
    category_target: Optional[str] = Field(None, description="Optional target label or category constraint.")


class QuantumTextMetricsSchema(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1: float
    training_time_seconds: Optional[float] = None
    prediction_time_seconds: Optional[float] = None


class QuantumMetadataSchema(BaseModel):
    framework: str
    backend: str
    qubits: int
    shots: int
    circuit_depth: int


class QuantumTextExperimentResponse(BaseModel):
    """
    Standardized, JSON-safe response for Quantum Text Intelligence.
    Contains both rich experimental evaluation metadata and backwards-compatible legacy fields.
    """

    task: str
    model: str
    prediction: Any
    confidence: Optional[float] = None
    metrics: Optional[QuantumTextMetricsSchema] = None
    quantum: QuantumMetadataSchema

    # Explainability & Pipeline Tracking
    pipeline_steps: Optional[List[str]] = None

    # Classical Baseline Comparison
    classical_baseline: Optional[Dict[str, Any]] = None

    # Backward-Compatibility Attributes for Existing Frontend & Test Fixtures
    input_text: str
    tokens: List[str]
    classical_features: List[float]
    quantum_probabilities: Dict[str, float]
    predicted_style: str
    classical_baseline_prediction: str
    classical_confidence: Optional[float] = None
    circuit_depth: int
    num_qubits: int
    execution_time_ms: float

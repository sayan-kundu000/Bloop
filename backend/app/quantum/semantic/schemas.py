"""
Bloop Quantum Semantic Intelligence Schemas
Pydantic schemas for pairwise text similarity, similarity matrix computation,
and classical vs quantum benchmarking requests and responses.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class SemanticAnalysisRequest(BaseModel):
    """Pairwise text semantic similarity request."""
    text_a: str = Field(..., min_length=1, max_length=1000, description="First text snippet for semantic comparison")
    text_b: str = Field(..., min_length=1, max_length=1000, description="Second text snippet for semantic comparison")
    method: Optional[str] = Field("hybrid", description="Analysis method: 'hybrid', 'classical', or 'quantum'")
    framework: Optional[str] = Field("qiskit", description="Quantum framework: 'qiskit' or 'pennylane'")
    num_qubits: int = Field(4, ge=2, le=8, description="Target quantum register size (2 to 8 qubits)")
    shots: int = Field(1024, ge=100, le=4096, description="Quantum simulation shot count")

    @field_validator("text_a", "text_b")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text snippet cannot be empty or whitespace-only.")
        return v.strip()


class SemanticAnalysisResponse(BaseModel):
    """Pairwise semantic comparison response preserving backward compatibility and enriching research metadata."""
    # Legacy backward-compatible fields
    text_a: str
    text_b: str
    quantum_kernel_similarity: float
    classical_cosine_similarity: float
    similarity_verdict: str
    divergence: float
    num_qubits: int
    circuit_depth: int
    execution_time_ms: float

    # Prompt 25 Enrichments
    method: str
    similarity_score: float
    classical_similarity: float
    quantum_similarity: Optional[float] = None
    hybrid_similarity: Optional[float] = None
    semantic_distance: float
    feature_dimension: int
    reduced_dimension: int
    representation_method: str
    reduction_method: str
    encoding_method: str
    quantum_framework: str
    quantum_backend: str
    shots: int
    experiment_id: Optional[str] = None
    pipeline_steps: Optional[List[str]] = None
    details: Optional[Dict[str, Any]] = None


class SemanticMatrixRequest(BaseModel):
    """Request for pairwise similarity matrix across a collection of texts."""
    texts: List[str] = Field(..., min_length=2, max_length=10, description="List of 2 to 10 texts for pairwise matrix analysis")
    method: Optional[str] = Field("hybrid", description="Analysis method: 'hybrid', 'classical', or 'quantum'")
    framework: Optional[str] = Field("qiskit", description="Quantum framework: 'qiskit' or 'pennylane'")
    num_qubits: int = Field(4, ge=2, le=8, description="Target quantum register size")
    shots: int = Field(1024, ge=100, le=4096, description="Quantum simulation shot count")

    @field_validator("texts")
    @classmethod
    def validate_texts(cls, v: List[str]) -> List[str]:
        cleaned = [t.strip() for t in v if t and t.strip()]
        if len(cleaned) < 2:
            raise ValueError("At least 2 non-empty texts are required for matrix analysis.")
        if len(cleaned) > 10:
            raise ValueError("Matrix analysis is bounded to a maximum of 10 texts to prevent computational explosion.")
        return cleaned


class SemanticMatrixResponse(BaseModel):
    """Pairwise similarity matrix output."""
    texts: List[str]
    matrix: List[List[float]]
    method: str
    num_texts: int
    total_comparisons: int
    execution_time_ms: float


class SemanticBenchmarkRequest(BaseModel):
    """Request for running empirical benchmark on reference semantic dataset."""
    num_qubits: int = Field(4, ge=2, le=8, description="Target quantum register size")
    shots: int = Field(1024, ge=100, le=4096, description="Quantum simulation shots")
    framework: Optional[str] = Field("qiskit", description="Quantum framework: 'qiskit' or 'pennylane'")


class SemanticBenchmarkResponse(BaseModel):
    """Empirical classical vs quantum semantic benchmark evaluation."""
    dataset_name: str
    sample_count: int
    classical_metrics: Dict[str, Any]
    quantum_metrics: Dict[str, Any]
    correlation_pearson: Optional[float] = None
    correlation_spearman: Optional[float] = None
    mae: Optional[float] = None
    rmse: Optional[float] = None
    honest_analysis: str
    execution_time_ms: float

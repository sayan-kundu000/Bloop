"""
Bloop Quantum Semantic Intelligence Domain Models
Defines domain enums, dataclasses, and value objects for semantic similarity,
quantum kernel evaluations, classical baselines, and benchmark metrics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SemanticMethod(str, Enum):
    """Supported semantic analysis methods."""
    HYBRID = "hybrid"
    CLASSICAL = "classical"
    QUANTUM = "quantum"


class SimilarityVerdict(str, Enum):
    """Calibrated neutral interpretation of similarity scores."""
    IDENTICAL = "Identical or Nearly Identical"
    STRONGLY_SIMILAR = "Strongly Similar"
    MODERATELY_SIMILAR = "Moderately Similar"
    DISSIMILAR = "Dissimilar"


class SemanticRepresentationType(str, Enum):
    """Classical semantic representation types."""
    TFIDF = "tfidf"
    LEXICAL = "lexical_deterministic"


class SemanticReductionType(str, Enum):
    """Feature reduction techniques for quantum dimension compatibility."""
    TRUNCATED_SVD = "truncated_svd"
    PCA = "pca"
    DETERMINISTIC_POOLING = "deterministic_pooling"


@dataclass
class PairwiseSemanticResult:
    """Domain model representing the comprehensive pairwise semantic comparison."""
    text_a: str
    text_b: str
    method: SemanticMethod
    similarity_score: float
    classical_similarity: float
    quantum_similarity: Optional[float]
    hybrid_similarity: Optional[float]
    similarity_verdict: SimilarityVerdict
    divergence: float
    semantic_distance: float
    num_qubits: int
    circuit_depth: int
    shots: int
    feature_dimension: int
    reduced_dimension: int
    representation_method: str
    reduction_method: str
    encoding_method: str
    quantum_framework: str
    quantum_backend: str
    execution_time_ms: float
    pipeline_steps: List[str] = field(default_factory=list)
    experiment_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticBenchmarkPair:
    """Pair of texts with a calibrated ground-truth semantic similarity score in [0.0, 1.0]."""
    text_a: str
    text_b: str
    expected_similarity: float
    category: str  # e.g. "identical", "paraphrase", "topical", "unrelated"


@dataclass
class SemanticBenchmarkMetrics:
    """Benchmark metrics evaluating semantic estimation against ground truth."""
    sample_count: int
    classical_mae: float
    classical_rmse: float
    classical_pearson: float
    classical_spearman: float
    quantum_mae: Optional[float]
    quantum_rmse: Optional[float]
    quantum_pearson: Optional[float]
    quantum_spearman: Optional[float]
    classical_latency_ms: float
    quantum_latency_ms: float
    honest_analysis: str


@dataclass
class SemanticMatrixResult:
    """Matrix of pairwise similarities for a list of texts."""
    texts: List[str]
    matrix: List[List[float]]
    method: SemanticMethod
    num_texts: int
    total_comparisons: int
    execution_time_ms: float

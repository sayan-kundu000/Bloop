"""
Bloop Hybrid Intelligence & Benchmarking Domain Models
Defines domain enums, metric structures, dataset descriptors,
and hybrid intelligence execution models.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class BenchmarkCategory(str, Enum):
    """Supported multi-category benchmark dimensions."""
    TEXT_CLASSIFICATION = "text_classification"      # Type A: Classical vs Quantum Text Classifier
    EMOTION_QNN = "emotion_qnn"                      # Type B: Classical Emotion vs Hybrid QNN
    SEMANTIC_SIMILARITY = "semantic_similarity"      # Type C: Cosine vs Quantum Kernel
    CIRCUIT_NOISE = "circuit_noise"                  # Type D: Ideal vs Noisy Aer Simulation
    HYBRID_SPEECH_PIPELINE = "hybrid_speech_pipeline"# Type E: End-to-end intelligence & acoustic settings


class ExperimentMode(str, Enum):
    """Operating modes for hybrid analysis and benchmarking."""
    ANALYSIS_ONLY = "analysis_only"
    ANALYSIS_AND_RECOMMENDATION = "analysis_and_recommendation"
    ANALYSIS_AND_SPEECH = "analysis_and_speech"


class FusionMethod(str, Enum):
    """Mathematical fusion strategies for combining classical and quantum representations."""
    SCORE_WEIGHTED = "score_weighted"                # S_hybrid = alpha * S_c + beta * S_q
    FEATURE_CONCATENATION = "feature_concatenation"  # z = [sqrt(alpha)*x_c, sqrt(beta)*x_q]
    DECISION_CONFIDENCE = "decision_confidence"      # Weighted confidence thresholding / argmax


class RecommendationPacing(str, Enum):
    """Pacing descriptors for acoustic speech delivery."""
    SLOW = "slow"
    MODERATE = "moderate"
    DYNAMIC = "dynamic"
    FAST = "fast"


@dataclass
class PipelineExecutionBreakdown:
    """Detailed wall-clock execution time breakdown across the pipeline."""
    classical_ms: float = 0.0
    quantum_ms: float = 0.0
    fusion_ms: float = 0.0
    recommendation_ms: float = 0.0
    tts_request_ms: Optional[float] = None
    total_ms: float = 0.0


@dataclass
class SpeechRecommendationDTO:
    """Provider-independent speech acoustic recommendation."""
    style: str = "balanced"
    speed: float = 1.0
    pitch: float = 1.0
    stability: float = 0.65
    similarity_boost: float = 0.75
    pacing: str = "moderate"
    reason: str = "Balanced standard delivery recommended."
    confidence: Optional[float] = None
    applied: bool = False
    target_voice_id: Optional[str] = None
    validated_compatible: bool = True


@dataclass
class BenchmarkMetrics:
    """Normalized empirical benchmark evaluation metrics."""
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mae: Optional[float] = None
    rmse: Optional[float] = None
    correlation: Optional[float] = None
    training_time_seconds: float = 0.0
    inference_time_seconds: float = 0.0
    qubits: int = 4
    shots: int = 1024
    circuit_depth: int = 0
    tvd: Optional[float] = None
    fidelity: Optional[float] = None


@dataclass
class DatasetMetadata:
    """Audit metadata for benchmark datasets."""
    dataset_name: str
    dataset_source: str
    dataset_version: str
    license: str
    task: str
    sample_count: int
    split_strategy: str
    train_count: int
    test_count: int
    random_seed: int


@dataclass
class HybridIntelligenceResult:
    """Result of hybrid intelligence analysis combining classical and quantum representations."""
    input_text: str
    classical_prediction: Dict[str, Any]
    quantum_prediction: Dict[str, Any]
    hybrid_prediction: Dict[str, Any]
    confidence: Optional[float]
    fusion_method: str
    fusion_weights: Dict[str, float]
    speech_recommendation: Optional[SpeechRecommendationDTO]
    execution_breakdown: PipelineExecutionBreakdown
    fallback_used: bool = False
    task: str = "affective_intelligence"


@dataclass
class MultiCategoryBenchmarkResult:
    """Normalized benchmark evaluation across classical, quantum, and hybrid candidates."""
    category: str
    dataset: DatasetMetadata
    classical_model: str
    quantum_model: str
    hybrid_model: Optional[str]
    classical_metrics: BenchmarkMetrics
    quantum_metrics: BenchmarkMetrics
    hybrid_metrics: Optional[BenchmarkMetrics]
    resource_usage: Dict[str, Any]
    honest_analysis: str
    quantum_advantage_detected: bool
    summary: str
    pipeline_breakdown: Optional[PipelineExecutionBreakdown] = None

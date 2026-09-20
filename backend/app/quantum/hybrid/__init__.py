"""
Bloop Hybrid Quantum-Classical ML & Intelligence Package
Provides hybrid feature encoding, variational classification, kernel estimation,
multi-category benchmarking, mathematical fusion, and provider-independent speech recommendations.
"""

from backend.app.quantum.hybrid.encoder import QuantumFeatureEncoder
from backend.app.quantum.hybrid.classifier import (
    HybridQuantumClassifier,
    HybridEvaluationResult,
    ModelMetrics,
)
from backend.app.quantum.hybrid.pipeline import HybridPipeline
from backend.app.quantum.hybrid.kernel import QuantumKernelEngine

from backend.app.quantum.hybrid.models import (
    BenchmarkCategory,
    ExperimentMode,
    FusionMethod,
    RecommendationPacing,
    PipelineExecutionBreakdown,
    SpeechRecommendationDTO,
    BenchmarkMetrics,
    DatasetMetadata,
    HybridIntelligenceResult,
    MultiCategoryBenchmarkResult,
)
from backend.app.quantum.hybrid.exceptions import (
    BenchmarkInvalidException,
    BenchmarkDatasetInvalidException,
    BenchmarkResourceLimitException,
    BenchmarkExecutionFailedException,
    BenchmarkMetricFailedException,
    HybridAnalysisFailedException,
    HybridFusionFailedException,
    RecommendationFailedException,
    RecommendationUnsupportedException,
    SpeechRecommendationInvalidException,
    SpeechCapabilityMismatchException,
)
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
from backend.app.quantum.hybrid.classical import (
    ClassicalTextBaseline,
    ClassicalEmotionBaseline,
    ClassicalSemanticBaseline,
)
from backend.app.quantum.hybrid.quantum import QuantumCandidateAdapter
from backend.app.quantum.hybrid.fusion import HybridFusionEngine
from backend.app.quantum.hybrid.recommendation import HybridSpeechRecommender
from backend.app.quantum.hybrid.speech_bridge import SpeechCapabilityBridge
from backend.app.quantum.hybrid.benchmark import BenchmarkRunner
from backend.app.quantum.hybrid.service import HybridIntelligenceService

__all__ = [
    # Legacy Exports (Prompt 22-26 Compatibility)
    "QuantumFeatureEncoder",
    "HybridQuantumClassifier",
    "HybridEvaluationResult",
    "ModelMetrics",
    "HybridPipeline",
    "QuantumKernelEngine",
    # Prompt 27 Domain Models & Enums
    "BenchmarkCategory",
    "ExperimentMode",
    "FusionMethod",
    "RecommendationPacing",
    "PipelineExecutionBreakdown",
    "SpeechRecommendationDTO",
    "BenchmarkMetrics",
    "DatasetMetadata",
    "HybridIntelligenceResult",
    "MultiCategoryBenchmarkResult",
    # Prompt 27 Exceptions
    "BenchmarkInvalidException",
    "BenchmarkDatasetInvalidException",
    "BenchmarkResourceLimitException",
    "BenchmarkExecutionFailedException",
    "BenchmarkMetricFailedException",
    "HybridAnalysisFailedException",
    "HybridFusionFailedException",
    "RecommendationFailedException",
    "RecommendationUnsupportedException",
    "SpeechRecommendationInvalidException",
    "SpeechCapabilityMismatchException",
    # Prompt 27 Schemas
    "FusionConfigSchema",
    "SpeechRecommendationSchema",
    "HybridAnalysisRequestSchema",
    "HybridAnalysisResponseSchema",
    "SpeechRecommendationRequestSchema",
    "MultiCategoryBenchmarkRequestSchema",
    "BenchmarkCategoryInfoSchema",
    "MultiCategoryBenchmarkResponseSchema",
    # Prompt 27 Engines & Services
    "ClassicalTextBaseline",
    "ClassicalEmotionBaseline",
    "ClassicalSemanticBaseline",
    "QuantumCandidateAdapter",
    "HybridFusionEngine",
    "HybridSpeechRecommender",
    "SpeechCapabilityBridge",
    "BenchmarkRunner",
    "HybridIntelligenceService",
]

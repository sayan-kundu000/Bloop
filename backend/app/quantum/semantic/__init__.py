"""
Bloop Quantum Semantic Intelligence Subsystem
Provides classical semantic baselines, TruncatedSVD feature reduction,
angle encoding, quantum state overlap fidelity kernels, and hybrid similarity analysis.
"""

from backend.app.quantum.semantic.classical import ClassicalSimilarityEngine
from backend.app.quantum.semantic.dataset import SemanticDatasetAdapter
from backend.app.quantum.semantic.evaluator import SemanticBenchmarkEvaluator
from backend.app.quantum.semantic.exceptions import (
    SemanticAnalysisFailedException,
    SemanticBenchmarkFailedException,
    SemanticDatasetInvalidException,
    SemanticEncodingFailedException,
    SemanticFeatureExtractionFailedException,
    SemanticInputInvalidException,
    SemanticKernelFailedException,
    SemanticReductionFailedException,
    SemanticResourceLimitException,
    SemanticSimilarityFailedException,
)
from backend.app.quantum.semantic.features import (
    LexicalFeatureProvider,
    SemanticFeatureExtractor,
    SemanticRepresentationProvider,
    TfidfFeatureProvider,
)
from backend.app.quantum.semantic.models import (
    PairwiseSemanticResult,
    SemanticBenchmarkMetrics,
    SemanticBenchmarkPair,
    SemanticMatrixResult,
    SemanticMethod,
    SemanticReductionType,
    SemanticRepresentationType,
    SimilarityVerdict,
)
from backend.app.quantum.semantic.normalization import SemanticAngleNormalizer
from backend.app.quantum.semantic.preprocess import SemanticPreprocessor
from backend.app.quantum.semantic.quantum_encoder import AngleFeatureEncoder
from backend.app.quantum.semantic.quantum_kernel import QuantumKernelEngine
from backend.app.quantum.semantic.reduction import SemanticDimensionalityReducer
from backend.app.quantum.semantic.schemas import (
    SemanticAnalysisRequest,
    SemanticAnalysisResponse,
    SemanticBenchmarkRequest,
    SemanticBenchmarkResponse,
    SemanticMatrixRequest,
    SemanticMatrixResponse,
)
from backend.app.quantum.semantic.service import QuantumSemanticService
from backend.app.quantum.semantic.similarity import SimilarityEngine

__all__ = [
    "QuantumSemanticService",
    "ClassicalSimilarityEngine",
    "QuantumKernelEngine",
    "SimilarityEngine",
    "SemanticFeatureExtractor",
    "TfidfFeatureProvider",
    "LexicalFeatureProvider",
    "SemanticRepresentationProvider",
    "SemanticDimensionalityReducer",
    "SemanticAngleNormalizer",
    "AngleFeatureEncoder",
    "SemanticPreprocessor",
    "SemanticDatasetAdapter",
    "SemanticBenchmarkEvaluator",
    "SemanticMethod",
    "SimilarityVerdict",
    "SemanticRepresentationType",
    "SemanticReductionType",
    "PairwiseSemanticResult",
    "SemanticBenchmarkPair",
    "SemanticBenchmarkMetrics",
    "SemanticMatrixResult",
    "SemanticAnalysisRequest",
    "SemanticAnalysisResponse",
    "SemanticMatrixRequest",
    "SemanticMatrixResponse",
    "SemanticBenchmarkRequest",
    "SemanticBenchmarkResponse",
    "SemanticAnalysisFailedException",
    "SemanticInputInvalidException",
    "SemanticFeatureExtractionFailedException",
    "SemanticReductionFailedException",
    "SemanticEncodingFailedException",
    "SemanticKernelFailedException",
    "SemanticSimilarityFailedException",
    "SemanticBenchmarkFailedException",
    "SemanticDatasetInvalidException",
    "SemanticResourceLimitException",
]

"""
Bloop Quantum Text Intelligence Subsystem
Modular, experimentally measurable text-to-quantum feature encoding and classification pipeline.
"""

from backend.app.quantum.text.circuit import TextQuantumCircuitBuilder
from backend.app.quantum.text.classifier import (
    ClassicalTextBaselineClassifier,
    HybridQuantumTextClassifier,
)
from backend.app.quantum.text.encoder import AngleFeatureEncoder, BaseQuantumFeatureEncoder
from backend.app.quantum.text.evaluator import QuantumTextBenchmarkEvaluator
from backend.app.quantum.text.exceptions import (
    ClassifierUnavailableException,
    DatasetInvalidException,
    FeatureDimensionTooLargeException,
    FeatureEncodingFailedException,
    FeatureReductionFailedException,
    ModelPredictionFailedException,
    ModelTrainingFailedException,
    QuantumClassificationFailedException,
    QuantumTextInvalidException,
    TextFeatureExtractionFailedException,
)
from backend.app.quantum.text.features import TextFeatureExtractor
from backend.app.quantum.text.models import (
    ClassificationMetrics,
    ClassificationTask,
    ClassifierStrategy,
    EncodingStrategy,
    PipelineExplanation,
    TextClassificationResult,
    TextFramework,
)
from backend.app.quantum.text.normalization import FeatureAngleNormalizer
from backend.app.quantum.text.preprocess import QuantumTextPreprocessor
from backend.app.quantum.text.reduction import TruncatedSVDReducer
from backend.app.quantum.text.schemas import (
    QuantumMetadataSchema,
    QuantumTextExperimentRequest,
    QuantumTextExperimentResponse,
    QuantumTextMetricsSchema,
)
from backend.app.quantum.text.service import QuantumTextService

__all__ = [
    "QuantumTextService",
    "QuantumTextPreprocessor",
    "TextFeatureExtractor",
    "TruncatedSVDReducer",
    "FeatureAngleNormalizer",
    "BaseQuantumFeatureEncoder",
    "AngleFeatureEncoder",
    "TextQuantumCircuitBuilder",
    "HybridQuantumTextClassifier",
    "ClassicalTextBaselineClassifier",
    "QuantumTextBenchmarkEvaluator",
    "QuantumTextExperimentRequest",
    "QuantumTextExperimentResponse",
    "QuantumTextMetricsSchema",
    "QuantumMetadataSchema",
    "ClassificationTask",
    "EncodingStrategy",
    "ClassifierStrategy",
    "TextFramework",
    "ClassificationMetrics",
    "PipelineExplanation",
    "TextClassificationResult",
    "QuantumTextInvalidException",
    "TextFeatureExtractionFailedException",
    "FeatureDimensionTooLargeException",
    "FeatureReductionFailedException",
    "FeatureEncodingFailedException",
    "ClassifierUnavailableException",
    "QuantumClassificationFailedException",
    "DatasetInvalidException",
    "ModelTrainingFailedException",
    "ModelPredictionFailedException",
]

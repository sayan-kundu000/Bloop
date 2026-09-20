"""
Bloop Hybrid Intelligence & Benchmarking Schemas
Defines request and response schemas for multi-category benchmarking,
hybrid feature fusion, and provider-independent speech recommendations.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator


class FusionConfigSchema(BaseModel):
    """Configuration for combining classical and quantum representations."""
    method: str = Field("score_weighted", description="Fusion method: 'score_weighted', 'feature_concatenation', 'decision_confidence'")
    classical_weight: float = Field(0.5, ge=0.0, le=1.0, description="Weight alpha assigned to classical representation")
    quantum_weight: float = Field(0.5, ge=0.0, le=1.0, description="Weight beta assigned to quantum representation")

    @model_validator(mode="after")
    def validate_weights(self) -> "FusionConfigSchema":
        total = self.classical_weight + self.quantum_weight
        if abs(total - 1.0) > 1e-4:
            raise ValueError(f"Fusion weights must sum to 1.0 (got {total:.4f}).")
        return self


class SpeechRecommendationSchema(BaseModel):
    """Provider-independent speech acoustic recommendation schema."""
    style: str = Field("balanced", description="Acoustic style delivery")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech rate multiplier")
    pitch: float = Field(1.0, ge=0.5, le=1.5, description="Speech pitch multiplier")
    stability: float = Field(0.65, ge=0.0, le=1.0, description="Voice stability/variability")
    similarity_boost: float = Field(0.75, ge=0.0, le=1.0, description="Clarity/similarity boost")
    pacing: str = Field("moderate", description="Delivery pacing: slow, moderate, dynamic, fast")
    reason: str = Field(..., description="Auditable reasoning behind recommended acoustic settings")
    confidence: Optional[float] = Field(None, description="Confidence of underlying prediction")
    applied: bool = Field(False, description="Whether the user explicitly applied this recommendation")
    target_voice_id: Optional[str] = Field(None, description="Dynamic voice ID evaluated for compatibility")
    validated_compatible: bool = Field(True, description="Whether recommendation was validated against voice capabilities")


class HybridAnalysisRequestSchema(BaseModel):
    """Request payload for hybrid intelligence text/affective analysis."""
    text: str = Field(..., min_length=1, max_length=1000, description="Input text to analyze")
    target_voice_id: Optional[str] = Field(None, description="Optional target voice for capability validation")
    language: Optional[str] = Field("en-US", description="Language code for synthesis matching")
    task: Optional[str] = Field("affective_intelligence", description="Analysis task: 'affective_intelligence', 'text_classification', 'semantic_tone'")
    fusion: Optional[FusionConfigSchema] = None
    include_recommendation: bool = Field(True, description="Whether to derive speech acoustic recommendation")
    num_qubits: int = Field(4, ge=2, le=6, description="Quantum feature register width")
    shots: int = Field(1024, ge=100, le=2048, description="Measurement shot count")


class HybridAnalysisResponseSchema(BaseModel):
    """Response payload for hybrid intelligence analysis."""
    input_text: str
    classical_prediction: Dict[str, Any]
    quantum_prediction: Dict[str, Any]
    hybrid_prediction: Dict[str, Any]
    confidence: Optional[float] = None
    fusion_method: str
    fusion_weights: Dict[str, float]
    speech_recommendation: Optional[SpeechRecommendationSchema] = None
    pipeline_breakdown: Dict[str, float]
    fallback_used: bool = False


class SpeechRecommendationRequestSchema(BaseModel):
    """Request to generate standalone speech recommendations from text or affective state."""
    text: str = Field(..., min_length=1, max_length=1000)
    target_voice_id: Optional[str] = None
    language: Optional[str] = "en-US"
    predicted_emotion: Optional[str] = None
    confidence: Optional[float] = None


class MultiCategoryBenchmarkRequestSchema(BaseModel):
    """Request to execute empirical benchmark across classical, quantum, and hybrid candidates."""
    category: str = Field("text_classification", description="Benchmark category: 'text_classification', 'emotion_qnn', 'semantic_similarity', 'circuit_noise', 'hybrid_speech_pipeline'")
    dataset_size: int = Field(40, ge=10, le=150, description="Bounded dataset sample count")
    test_split: float = Field(0.25, ge=0.1, le=0.5, description="Hold-out evaluation split ratio")
    num_qubits: int = Field(4, ge=2, le=6, description="Quantum circuit register width")
    shots: int = Field(512, ge=100, le=2048, description="Simulator shot count")
    random_seed: int = Field(42, ge=0, le=10000, description="Deterministic seed for reproducibility")
    classical_weight: float = Field(0.5, ge=0.0, le=1.0)
    quantum_weight: float = Field(0.5, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_weights(self) -> "MultiCategoryBenchmarkRequestSchema":
        total = self.classical_weight + self.quantum_weight
        if abs(total - 1.0) > 1e-4:
            raise ValueError(f"Fusion weights must sum to 1.0 (got {total:.4f}).")
        return self


class BenchmarkCategoryInfoSchema(BaseModel):
    """Descriptor for a supported benchmark category."""
    category: str
    name: str
    description: str
    classical_baseline: str
    quantum_candidate: str
    measured_metrics: List[str]


class MultiCategoryBenchmarkResponseSchema(BaseModel):
    """Normalized empirical benchmark evaluation response."""
    category: str
    dataset: Dict[str, Any]
    classical_model: str
    quantum_model: str
    hybrid_model: Optional[str] = None
    classical_metrics: Dict[str, Any]
    quantum_metrics: Dict[str, Any]
    hybrid_metrics: Optional[Dict[str, Any]] = None
    resource_usage: Dict[str, Any]
    honest_analysis: str
    quantum_advantage_detected: bool
    summary: str
    pipeline_breakdown: Optional[Dict[str, float]] = None
    speech_recommendation: Optional[SpeechRecommendationSchema] = None

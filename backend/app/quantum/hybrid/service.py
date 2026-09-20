"""
Bloop Hybrid Intelligence Service
Orchestrates hybrid text and affective analysis, multi-category benchmarking,
transparent mathematical fusion, speech recommendations, and multi-tenant persistence.
"""

import time
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.quantum.config import quantum_config
from backend.app.quantum.hybrid.benchmark import BenchmarkRunner
from backend.app.quantum.hybrid.classical import ClassicalEmotionBaseline
from backend.app.quantum.hybrid.fusion import HybridFusionEngine
from backend.app.quantum.hybrid.models import (
    BenchmarkCategory,
    PipelineExecutionBreakdown,
)
from backend.app.quantum.hybrid.quantum import QuantumCandidateAdapter
from backend.app.quantum.hybrid.recommendation import HybridSpeechRecommender
from backend.app.quantum.hybrid.schemas import (
    BenchmarkCategoryInfoSchema,
    HybridAnalysisRequestSchema,
    HybridAnalysisResponseSchema,
    MultiCategoryBenchmarkRequestSchema,
    MultiCategoryBenchmarkResponseSchema,
    SpeechRecommendationRequestSchema,
    SpeechRecommendationSchema,
)
from backend.app.quantum.hybrid.speech_bridge import SpeechCapabilityBridge
from backend.app.repositories.quantum_repository import QuantumRepository


class HybridIntelligenceService:
    """Central orchestrator for Bloop's Hybrid Quantum-Classical Intelligence Subsystem."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.repo = QuantumRepository(db) if db is not None else None
        self.benchmark_runner = BenchmarkRunner()
        self.recommender = HybridSpeechRecommender()
        self.speech_bridge = SpeechCapabilityBridge(db)
        self.quantum_adapter = QuantumCandidateAdapter(db)

    def analyze_hybrid(
        self,
        req: HybridAnalysisRequestSchema,
        user_id: Optional[int] = None,
    ) -> HybridAnalysisResponseSchema:
        """
        Executes end-to-end hybrid analysis:
        1. Classical baseline analysis
        2. Quantum state-space analysis
        3. Mathematical fusion
        4. Optional acoustic speech recommendation
        5. Safe persistence
        """
        classical_weight = req.fusion.classical_weight if req.fusion else quantum_config.hybrid_default_classical_weight
        quantum_weight = req.fusion.quantum_weight if req.fusion else quantum_config.hybrid_default_quantum_weight
        fusion_method = req.fusion.method if req.fusion else "score_weighted"

        t0_total = time.perf_counter()

        # 1. Classical Stage
        t0_c = time.perf_counter()
        c_baseline = ClassicalEmotionBaseline()
        # Fast fit on representative samples
        from backend.app.quantum.hybrid.benchmark import EMOTION_BENCHMARK_CORPUS
        c_baseline.fit([d[0] for d in EMOTION_BENCHMARK_CORPUS], [d[1] for d in EMOTION_BENCHMARK_CORPUS])
        c_preds, c_prob_list, _ = c_baseline.predict([req.text])
        c_pred = c_preds[0]
        c_probs = c_prob_list[0]
        t_c = time.perf_counter() - t0_c

        # 2. Quantum Stage (with classical fallback)
        t0_q = time.perf_counter()
        fallback_used = False
        q_pred = "neutral"
        q_probs = {"neutral": 1.0, "joy": 0.0, "sadness": 0.0, "anger": 0.0}

        try:
            if not quantum_config.enabled:
                fallback_used = True
            else:
                q_pred, q_probs, _ = self.quantum_adapter.evaluate_emotion(
                    text=req.text,
                    num_qubits=req.num_qubits,
                    shots=req.shots,
                )
        except Exception as q_err:
            logger.warning(f"Quantum analysis failed; falling back to classical baseline: {q_err}")
            fallback_used = True
            q_probs = c_probs.copy()
            q_pred = c_pred
        t_q = time.perf_counter() - t0_q

        # 3. Fusion Stage
        t0_f = time.perf_counter()
        if fallback_used:
            fused_class = c_pred
            fused_conf = c_probs.get(c_pred, 0.85)
            fused_dist = c_probs
        else:
            fused_class, fused_conf, fused_dist = HybridFusionEngine.fuse_scores(
                c_probs, q_probs, alpha=classical_weight, beta=quantum_weight
            )
        t_f = time.perf_counter() - t0_f

        # 4. Optional Speech Recommendation Stage
        rec_schema = None
        t_r = 0.0
        if req.include_recommendation:
            t0_r = time.perf_counter()
            rec_dto = self.recommender.generate_recommendation(
                predicted_class=fused_class,
                class_scores=fused_dist,
                confidence=fused_conf,
                target_voice_id=req.target_voice_id,
            )
            # Enrich via dynamic voice capability check
            rec_dto = self.speech_bridge.validate_and_enrich_recommendation(
                recommendation=rec_dto,
                voice_id=req.target_voice_id,
                language=req.language or "en-US",
            )
            rec_schema = SpeechRecommendationSchema(
                style=rec_dto.style,
                speed=rec_dto.speed,
                pitch=rec_dto.pitch,
                stability=rec_dto.stability,
                similarity_boost=rec_dto.similarity_boost,
                pacing=rec_dto.pacing,
                reason=rec_dto.reason,
                confidence=rec_dto.confidence,
                applied=rec_dto.applied,
                target_voice_id=rec_dto.target_voice_id,
                validated_compatible=rec_dto.validated_compatible,
            )
            t_r = time.perf_counter() - t0_r

        total_time = time.perf_counter() - t0_total

        breakdown = {
            "classical_ms": round(t_c * 1000, 2),
            "quantum_ms": round(t_q * 1000, 2),
            "fusion_ms": round(t_f * 1000, 2),
            "recommendation_ms": round(t_r * 1000, 2),
            "total_ms": round(total_time * 1000, 2),
        }

        response = HybridAnalysisResponseSchema(
            input_text=req.text,
            classical_prediction={"class": c_pred, "scores": c_probs},
            quantum_prediction={"class": q_pred, "scores": q_probs},
            hybrid_prediction={"class": fused_class, "scores": fused_dist},
            confidence=fused_conf,
            fusion_method=fusion_method,
            fusion_weights={"classical": classical_weight, "quantum": quantum_weight},
            speech_recommendation=rec_schema,
            pipeline_breakdown=breakdown,
            fallback_used=fallback_used,
        )

        # 5. Safe Persistence
        self._safe_persist(
            experiment_type="hybrid_analysis",
            title=f"Hybrid Intelligence Analysis: '{req.text[:40]}...'",
            input_payload=req.model_dump(),
            results=response.model_dump(),
            user_id=user_id,
            qubit_count=req.num_qubits,
            execution_time_ms=breakdown["total_ms"],
        )

        return response

    def run_benchmark(
        self,
        req: MultiCategoryBenchmarkRequestSchema,
        user_id: Optional[int] = None,
    ) -> MultiCategoryBenchmarkResponseSchema:
        """Executes a multi-category empirical benchmark and persists the results."""
        res = self.benchmark_runner.run_benchmark(
            category=req.category,
            dataset_size=req.dataset_size,
            test_split=req.test_split,
            num_qubits=req.num_qubits,
            shots=req.shots,
            random_seed=req.random_seed,
            classical_weight=req.classical_weight,
            quantum_weight=req.quantum_weight,
        )

        breakdown_dict = None
        if res.pipeline_breakdown:
            breakdown_dict = {
                "classical_ms": res.pipeline_breakdown.classical_ms,
                "quantum_ms": res.pipeline_breakdown.quantum_ms,
                "fusion_ms": res.pipeline_breakdown.fusion_ms,
                "recommendation_ms": res.pipeline_breakdown.recommendation_ms,
                "total_ms": res.pipeline_breakdown.total_ms,
            }

        rec_schema = None
        if res.category == BenchmarkCategory.HYBRID_SPEECH_PIPELINE.value:
            rec_dto = self.recommender.generate_recommendation(
                predicted_class="joy",
                class_scores={"joy": 0.70, "neutral": 0.20},
                confidence=0.70,
            )
            rec_schema = SpeechRecommendationSchema(
                style=rec_dto.style,
                speed=rec_dto.speed,
                pitch=rec_dto.pitch,
                stability=rec_dto.stability,
                similarity_boost=rec_dto.similarity_boost,
                pacing=rec_dto.pacing,
                reason=rec_dto.reason,
                confidence=rec_dto.confidence,
                applied=rec_dto.applied,
                target_voice_id=rec_dto.target_voice_id,
                validated_compatible=rec_dto.validated_compatible,
            )

        response = MultiCategoryBenchmarkResponseSchema(
            category=res.category,
            dataset={
                "dataset_name": res.dataset.dataset_name,
                "dataset_source": res.dataset.dataset_source,
                "dataset_version": res.dataset.dataset_version,
                "license": res.dataset.license,
                "task": res.dataset.task,
                "sample_count": res.dataset.sample_count,
                "split_strategy": res.dataset.split_strategy,
                "train_count": res.dataset.train_count,
                "test_count": res.dataset.test_count,
                "random_seed": res.dataset.random_seed,
            },
            classical_model=res.classical_model,
            quantum_model=res.quantum_model,
            hybrid_model=res.hybrid_model,
            classical_metrics={
                "accuracy": res.classical_metrics.accuracy,
                "precision": res.classical_metrics.precision,
                "recall": res.classical_metrics.recall,
                "f1_score": res.classical_metrics.f1_score,
                "mae": res.classical_metrics.mae,
                "rmse": res.classical_metrics.rmse,
                "correlation": res.classical_metrics.correlation,
                "training_time_seconds": res.classical_metrics.training_time_seconds,
                "inference_time_seconds": res.classical_metrics.inference_time_seconds,
                "qubits": res.classical_metrics.qubits,
                "shots": res.classical_metrics.shots,
                "circuit_depth": res.classical_metrics.circuit_depth,
                "tvd": res.classical_metrics.tvd,
                "fidelity": res.classical_metrics.fidelity,
            },
            quantum_metrics={
                "accuracy": res.quantum_metrics.accuracy,
                "precision": res.quantum_metrics.precision,
                "recall": res.quantum_metrics.recall,
                "f1_score": res.quantum_metrics.f1_score,
                "mae": res.quantum_metrics.mae,
                "rmse": res.quantum_metrics.rmse,
                "correlation": res.quantum_metrics.correlation,
                "training_time_seconds": res.quantum_metrics.training_time_seconds,
                "inference_time_seconds": res.quantum_metrics.inference_time_seconds,
                "qubits": res.quantum_metrics.qubits,
                "shots": res.quantum_metrics.shots,
                "circuit_depth": res.quantum_metrics.circuit_depth,
                "tvd": res.quantum_metrics.tvd,
                "fidelity": res.quantum_metrics.fidelity,
            },
            hybrid_metrics={
                "accuracy": res.hybrid_metrics.accuracy,
                "precision": res.hybrid_metrics.precision,
                "recall": res.hybrid_metrics.recall,
                "f1_score": res.hybrid_metrics.f1_score,
                "mae": res.hybrid_metrics.mae,
                "rmse": res.hybrid_metrics.rmse,
                "correlation": res.hybrid_metrics.correlation,
                "inference_time_seconds": res.hybrid_metrics.inference_time_seconds,
                "qubits": res.hybrid_metrics.qubits,
                "shots": res.hybrid_metrics.shots,
                "circuit_depth": res.hybrid_metrics.circuit_depth,
            } if res.hybrid_metrics else None,
            resource_usage=res.resource_usage,
            honest_analysis=res.honest_analysis,
            quantum_advantage_detected=res.quantum_advantage_detected,
            summary=res.summary,
            pipeline_breakdown=breakdown_dict,
            speech_recommendation=rec_schema,
        )

        # Safe persistence
        self._safe_persist(
            experiment_type="benchmark",
            title=f"Multi-Category Benchmark: {res.category}",
            input_payload=req.model_dump(),
            results=response.model_dump(),
            user_id=user_id,
            qubit_count=req.num_qubits,
            execution_time_ms=res.quantum_metrics.inference_time_seconds * 1000,
        )

        return response

    def generate_recommendation(
        self,
        req: SpeechRecommendationRequestSchema,
        user_id: Optional[int] = None,
    ) -> SpeechRecommendationSchema:
        """Standalone speech recommendation generation from text or emotional label."""
        if req.predicted_emotion:
            emotion = req.predicted_emotion.lower()
            conf = req.confidence or 0.85
            scores = {emotion: conf}
        else:
            c_baseline = ClassicalEmotionBaseline()
            from backend.app.quantum.hybrid.benchmark import EMOTION_BENCHMARK_CORPUS
            c_baseline.fit([d[0] for d in EMOTION_BENCHMARK_CORPUS], [d[1] for d in EMOTION_BENCHMARK_CORPUS])
            preds, prob_list, _ = c_baseline.predict([req.text])
            emotion = preds[0]
            scores = prob_list[0]
            conf = scores.get(emotion, 0.85)

        rec_dto = self.recommender.generate_recommendation(
            predicted_class=emotion,
            class_scores=scores,
            confidence=conf,
            target_voice_id=req.target_voice_id,
        )
        rec_dto = self.speech_bridge.validate_and_enrich_recommendation(
            recommendation=rec_dto,
            voice_id=req.target_voice_id,
            language=req.language or "en-US",
        )

        return SpeechRecommendationSchema(
            style=rec_dto.style,
            speed=rec_dto.speed,
            pitch=rec_dto.pitch,
            stability=rec_dto.stability,
            similarity_boost=rec_dto.similarity_boost,
            pacing=rec_dto.pacing,
            reason=rec_dto.reason,
            confidence=rec_dto.confidence,
            applied=rec_dto.applied,
            target_voice_id=rec_dto.target_voice_id,
            validated_compatible=rec_dto.validated_compatible,
        )

    @staticmethod
    def get_supported_categories() -> List[BenchmarkCategoryInfoSchema]:
        """Returns catalog of supported benchmark categories."""
        return [
            BenchmarkCategoryInfoSchema(
                category=BenchmarkCategory.TEXT_CLASSIFICATION.value,
                name="Quantum Text Classification (Type A)",
                description="Compares TF-IDF Logistic Regression against Variational Quantum Classifier (VQC) with angle encoding and entanglement.",
                classical_baseline="Logistic Regression (TF-IDF)",
                quantum_candidate="Variational Quantum Classifier (Qiskit Aer)",
                measured_metrics=["accuracy", "precision", "recall", "f1_score", "training_time", "inference_latency"],
            ),
            BenchmarkCategoryInfoSchema(
                category=BenchmarkCategory.EMOTION_QNN.value,
                name="Quantum Emotion Intelligence (Type B)",
                description="Compares Multinomial Logistic Regression against PennyLane Hybrid QNN for multi-class affective classification.",
                classical_baseline="Multinomial Logistic Regression",
                quantum_candidate="Hybrid Emotion QNN (PennyLane default.qubit)",
                measured_metrics=["accuracy", "precision", "recall", "f1_score", "training_time", "inference_latency"],
            ),
            BenchmarkCategoryInfoSchema(
                category=BenchmarkCategory.SEMANTIC_SIMILARITY.value,
                name="Quantum Semantic Intelligence (Type C)",
                description="Compares TF-IDF Cosine Similarity against Quantum Kernel State Fidelity with convex hybrid fusion.",
                classical_baseline="Cosine Similarity (TF-IDF)",
                quantum_candidate="Quantum Kernel State Fidelity (Qiskit ML)",
                measured_metrics=["mae", "rmse", "pearson_correlation", "inference_latency"],
            ),
            BenchmarkCategoryInfoSchema(
                category=BenchmarkCategory.CIRCUIT_NOISE.value,
                name="Quantum Circuit & Noise Simulation (Type D)",
                description="Compares Ideal Unitary Dynamics against Noisy Aer Simulation across Kraus error channels.",
                classical_baseline="Ideal Aer Simulator (Unitary)",
                quantum_candidate="Noisy Aer Simulator (Depolarizing / Thermal)",
                measured_metrics=["total_variation_distance", "classical_fidelity", "entropy_shift", "latency"],
            ),
            BenchmarkCategoryInfoSchema(
                category=BenchmarkCategory.HYBRID_SPEECH_PIPELINE.value,
                name="Hybrid Speech Intelligence Pipeline (Type E)",
                description="Evaluates complete end-to-end intelligence overhead: classical + quantum + fusion + acoustic recommendation.",
                classical_baseline="Classical Emotion Extraction",
                quantum_candidate="Quantum Affective Analysis",
                measured_metrics=["classical_ms", "quantum_ms", "fusion_ms", "recommendation_ms", "total_pipeline_ms"],
            ),
        ]

    def _safe_persist(self, **kwargs: Any) -> None:
        """Safely persists experiment logs without raising if database unavailable."""
        if self.repo is not None:
            try:
                self.repo.create(**kwargs)
            except Exception as e:
                logger.warning(f"Could not persist hybrid experiment record: {e}")

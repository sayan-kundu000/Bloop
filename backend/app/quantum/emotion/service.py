"""
Quantum Emotion Intelligence — Central Service Orchestrator
Coordinates text validation, affective feature engineering, hybrid QNN execution,
emotion classification, speech recommendation, and multi-tenant persistence.
"""

import time
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.quantum.config import quantum_config
from backend.app.quantum.emotion.preprocess import EmotionTextPreprocessor
from backend.app.quantum.emotion.features import EmotionFeatureExtractor
from backend.app.quantum.emotion.reduction import EmotionSVDReducer
from backend.app.quantum.emotion.normalization import EmotionAngleNormalizer
from backend.app.quantum.emotion.encoder import EmotionAngleEncoder
from backend.app.quantum.emotion.qnn import HybridEmotionQNN
from backend.app.quantum.emotion.classifier import HybridEmotionClassifier, ClassicalEmotionBaseline
from backend.app.quantum.emotion.dataset import EmotionDataset
from backend.app.quantum.emotion.evaluator import EmotionBenchmarkEvaluator
from backend.app.quantum.emotion.recommender import SpeechRecommendationService
from backend.app.quantum.emotion.schemas import (
    EmotionExperimentRequest,
    EmotionExperimentResponse,
    SpeechRecommendationPayload,
)
from backend.app.quantum.emotion.models import EmotionClassificationResult, SpeechRecommendation
from backend.app.quantum.emotion.exceptions import EmotionAnalysisFailedException
from backend.app.repositories.quantum_experiment import QuantumExperimentRepository


class QuantumEmotionService:
    """
    Central Coordinator for Quantum Emotion Intelligence.
    Decoupled from HTTP routers and ElevenLabs speech synthesis.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.preprocessor = EmotionTextPreprocessor()
        self.recommender = SpeechRecommendationService()
        self.dataset = EmotionDataset()

        # Shared pipeline components
        self.extractor: Optional[EmotionFeatureExtractor] = None
        self.reducer: Optional[EmotionSVDReducer] = None
        self.normalizer: Optional[EmotionAngleNormalizer] = None
        self.classifier: Optional[HybridEmotionClassifier] = None
        self.classical_model: Optional[ClassicalEmotionBaseline] = None
        self.latest_metrics: Optional[Dict[str, Any]] = None
        self.latest_classical_summary: Optional[Dict[str, Any]] = None

        self._ensure_initialized()

    def _ensure_initialized(self):
        """Initializes and fits pipeline on training split with zero data leakage."""
        if self.classifier is None:
            evaluator = EmotionBenchmarkEvaluator(dataset=self.dataset, num_qubits=quantum_config.emotion_qubits)
            q_metrics, c_summary, q_clf, c_clf, ext, red, norm = evaluator.run_benchmark()
            self.classifier = q_clf
            self.classical_model = c_clf
            self.extractor = ext
            self.reducer = red
            self.normalizer = norm
            self.latest_metrics = q_metrics.to_dict()
            self.latest_classical_summary = c_summary

    def analyze_emotion(
        self,
        req: EmotionExperimentRequest,
        user_id: Optional[int] = None,
    ) -> EmotionExperimentResponse:
        """
        Executes end-to-end Quantum Emotion Intelligence analysis for an input text.
        """
        start_time = time.perf_counter()

        # 1. Text preprocessing and validation
        cleaned_text = self.preprocessor.preprocess(req.text)

        # 2. Classical feature extraction
        X_sparse = self.extractor.transform([cleaned_text])

        # 3. Dimensionality reduction (TruncatedSVD)
        X_reduced = self.reducer.transform(X_sparse)

        # 4. Continuous angle normalization [0, pi]
        X_angles = self.normalizer.transform(X_reduced)

        # 5. Angle feature encoding on quantum register
        encoder = EmotionAngleEncoder(num_qubits=req.num_qubits)
        encoded_angles = encoder.encode(X_angles[0])

        # 6. Hybrid QNN inference & classification
        pred_emotion, scores, confidence, entropy = self.classifier.predict_single(encoded_angles)

        # 7. Classical baseline prediction
        pred_classical, conf_classical = self.classical_model.predict_single(X_reduced[0])

        # 8. Optional Speech Recommendation
        recommendation_payload = None
        if req.include_recommendation:
            try:
                rec: SpeechRecommendation = self.recommender.generate_recommendation(
                    predicted_emotion=pred_emotion,
                    emotion_scores=scores,
                    confidence=confidence,
                )
                recommendation_payload = SpeechRecommendationPayload(
                    style=rec.style,
                    speed=rec.speed,
                    pitch=rec.pitch,
                    stability=rec.stability,
                    similarity_boost=rec.similarity_boost,
                    pacing=rec.pacing,
                    reason=rec.reason,
                    confidence=rec.confidence,
                    applied=rec.applied,
                )
            except Exception:
                # Fallback: recommendation failure never destroys emotion analysis result
                recommendation_payload = None

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        circuit_depth = self.classifier.qnn.get_circuit_depth()

        quantum_probs = {f"|{emo}>": score for emo, score in scores.items()}

        response = EmotionExperimentResponse(
            input_text=cleaned_text,
            detected_emotion=pred_emotion,
            emotion_scores=scores,
            quantum_probabilities=quantum_probs,
            hybrid_qnn_confidence=confidence,
            classical_baseline_emotion=pred_classical,
            classical_confidence=conf_classical,
            entanglement_entropy=entropy,
            circuit_depth=circuit_depth,
            num_qubits=req.num_qubits,
            execution_time_ms=execution_time_ms,
            speech_recommendation=recommendation_payload,
            metrics=self.latest_metrics,
            classical_baseline=self.latest_classical_summary,
            quantum={
                "framework": req.framework or "pennylane",
                "circuit_depth": circuit_depth,
                "num_qubits": req.num_qubits,
                "shots": req.shots,
                "entanglement_entropy": entropy,
            },
            pipeline_steps=[
                "text_validation",
                "affective_feature_extraction",
                "truncated_svd_reduction",
                "angle_normalization",
                "hybrid_qnn_variational_circuit",
                "quantum_measurement_pauliz",
                "classical_decision_head",
                "speech_recommendation",
            ],
        )

        # 9. Multi-tenant experiment persistence
        if self.db and user_id:
            self._safe_persist(
                user_id=user_id,
                req=req,
                res=response,
                qubits=req.num_qubits,
                depth=circuit_depth,
                exec_time=execution_time_ms,
            )

        return response

    def _safe_persist(
        self,
        user_id: int,
        req: EmotionExperimentRequest,
        res: EmotionExperimentResponse,
        qubits: int,
        depth: int,
        exec_time: float,
    ) -> None:
        """Persists the experiment record strictly isolated by user_id."""
        try:
            repo = QuantumExperimentRepository(self.db)
            repo.create(
                user_id=user_id,
                experiment_type="emotion",
                title=f"Quantum Emotion QNN: {res.detected_emotion.capitalize()}",
                simulator=req.framework or "pennylane",
                qubit_count=qubits,
                circuit_depth=depth,
                input_payload={"text_length": len(req.text), "framework": req.framework, "shots": req.shots},
                results=res.model_dump(),
                execution_time_ms=exec_time,
            )
        except Exception:
            # Persistence failure never blocks returning the analytical response
            pass

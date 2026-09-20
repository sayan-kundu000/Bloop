"""
Bloop Quantum Semantic Intelligence Service
Orchestrates pairwise semantic similarity analysis, matrix comparisons,
classical baselines, quantum kernel evaluations, and multi-tenant experiment persistence.
"""

import logging
import time
from typing import Any, Dict, List, Optional
import numpy as np
from sqlalchemy.orm import Session

from backend.app.quantum.config import quantum_config
from backend.app.quantum.exceptions import QuantumDisabledException
from backend.app.quantum.semantic.classical import ClassicalSimilarityEngine
from backend.app.quantum.semantic.dataset import SemanticDatasetAdapter
from backend.app.quantum.semantic.evaluator import SemanticBenchmarkEvaluator
from backend.app.quantum.semantic.exceptions import (
    SemanticAnalysisFailedException,
    SemanticResourceLimitException,
)
from backend.app.quantum.semantic.features import SemanticFeatureExtractor, TfidfFeatureProvider
from backend.app.quantum.semantic.models import SemanticMethod, SimilarityVerdict
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
from backend.app.quantum.semantic.similarity import SimilarityEngine
from backend.app.repositories.quantum_experiment import QuantumExperimentRepository

logger = logging.getLogger(__name__)


class QuantumSemanticService:
    """
    Central orchestrator for the Bloop Quantum Semantic Intelligence subsystem.
    Completely decoupled from the core Text-to-Speech generation pipeline.
    """

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.repo = QuantumExperimentRepository(db) if db is not None else None
        self.preprocessor = SemanticPreprocessor()
        self.feature_extractor = SemanticFeatureExtractor()

    def analyze_similarity(
        self,
        req: SemanticAnalysisRequest,
        user_id: Optional[int] = None,
    ) -> SemanticAnalysisResponse:
        """
        Executes text-to-text semantic similarity analysis using classical baseline,
        quantum kernel fidelity, or hybrid comparative evaluation.
        """
        start_time = time.perf_counter()
        pipeline_steps = ["1. Text Validation & Preprocessing"]

        # 1. Text Validation & Preprocessing
        clean_a, clean_b = self.preprocessor.validate_pair(req.text_a, req.text_b)
        is_identical = (clean_a.strip().lower() == clean_b.strip().lower())

        # Parse and validate method
        method_str = (req.method or "hybrid").lower()
        try:
            method = SemanticMethod(method_str)
        except ValueError:
            method = SemanticMethod.HYBRID

        num_qubits = max(2, min(req.num_qubits, quantum_config.max_qubits))
        shots = max(100, min(req.shots, quantum_config.max_shots))
        framework = (req.framework or "qiskit").lower()

        # 2. Classical Feature Extraction
        pipeline_steps.append("2. Classical TF-IDF Feature Extraction")
        feat_a, feat_b = self.feature_extractor.extract_pair(clean_a, clean_b)
        feature_dim = len(feat_a)

        # 3. Classical Cosine Similarity Baseline
        pipeline_steps.append("3. Classical Cosine Similarity Baseline")
        classical_sim = ClassicalSimilarityEngine.compute_cosine_similarity(
            feat_a, feat_b, raw_text_a=clean_a, raw_text_b=clean_b
        )

        quantum_sim: Optional[float] = None
        circuit_depth = 0
        reduced_dim = num_qubits
        quantum_backend = "none"

        # 4. Quantum Kernel Path (if method is hybrid or quantum)
        if method in (SemanticMethod.HYBRID, SemanticMethod.QUANTUM):
            if not quantum_config.enabled:
                raise QuantumDisabledException("Quantum computing subsystem is currently disabled.")

            pipeline_steps.append("4. Dimensionality Reduction (TruncatedSVD / Pooling)")
            reducer = SemanticDimensionalityReducer(target_dim=num_qubits)
            red_a, red_b = reducer.reduce_pair(feat_a, feat_b)

            pipeline_steps.append("5. Angle Normalization ([0, pi])")
            normalizer = SemanticAngleNormalizer(target_dim=num_qubits)
            angles_a, angles_b = normalizer.normalize_pair(red_a, red_b)

            pipeline_steps.append(f"6. Quantum Kernel Fidelity Simulation ({framework.capitalize()})")
            kernel_engine = QuantumKernelEngine(num_qubits=num_qubits)
            q_fidelity, depth, quantum_backend = kernel_engine.evaluate(
                angles_a, angles_b, framework=framework, shots=shots
            )
            quantum_sim = q_fidelity
            circuit_depth = depth
        else:
            pipeline_steps.append("4. Quantum Execution Skipped (Classical-Only Mode)")

        # 5. Similarity Resolution & Verdict
        pipeline_steps.append("7. Similarity Resolution & Neutral Interpretation")
        primary_score, hybrid_sim, divergence, verdict = SimilarityEngine.resolve_score_and_verdict(
            method=method,
            classical_sim=classical_sim,
            quantum_sim=quantum_sim,
            is_identical_text=is_identical,
        )

        semantic_dist = ClassicalSimilarityEngine.compute_semantic_distance(primary_score)
        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 6. Multi-Tenant Experiment Persistence
        exp_id = None
        if self.repo is not None:
            try:
                exp = self.repo.create(
                    experiment_type="quantum_semantic",
                    title=f"Semantic Analysis: '{clean_a[:20]}' vs '{clean_b[:20]}'",
                    input_payload={
                        "text_a": clean_a,
                        "text_b": clean_b,
                        "method": method.value,
                        "framework": framework,
                        "num_qubits": num_qubits,
                        "shots": shots,
                    },
                    results={
                        "primary_score": primary_score,
                        "classical_similarity": classical_sim,
                        "quantum_similarity": quantum_sim,
                        "hybrid_similarity": hybrid_sim,
                        "divergence": divergence,
                        "verdict": verdict.value,
                        "circuit_depth": circuit_depth,
                    },
                    user_id=user_id,
                    qubit_count=num_qubits,
                    circuit_depth=circuit_depth,
                    execution_time_ms=execution_time_ms,
                    simulator=quantum_backend,
                )
                exp_id = str(exp.id)
            except Exception as e:
                logger.warning(f"Failed to persist semantic experiment record: {e}")

        return SemanticAnalysisResponse(
            text_a=clean_a,
            text_b=clean_b,
            quantum_kernel_similarity=round(quantum_sim if quantum_sim is not None else classical_sim, 4),
            classical_cosine_similarity=round(classical_sim, 4),
            similarity_verdict=verdict.value,
            divergence=round(divergence, 4),
            num_qubits=num_qubits,
            circuit_depth=circuit_depth,
            execution_time_ms=execution_time_ms,
            method=method.value,
            similarity_score=round(primary_score, 4),
            classical_similarity=round(classical_sim, 4),
            quantum_similarity=round(quantum_sim, 4) if quantum_sim is not None else None,
            hybrid_similarity=round(hybrid_sim, 4) if hybrid_sim is not None else None,
            semantic_distance=round(semantic_dist, 4),
            feature_dimension=feature_dim,
            reduced_dimension=reduced_dim,
            representation_method=self.feature_extractor.representation_name,
            reduction_method="TruncatedSVD / Deterministic Band Pooling",
            encoding_method="Continuous Angle Encoding (Ry)",
            quantum_framework=framework,
            quantum_backend=quantum_backend,
            shots=shots,
            experiment_id=exp_id,
            pipeline_steps=pipeline_steps,
        )

    def compute_matrix(
        self,
        req: SemanticMatrixRequest,
        user_id: Optional[int] = None,
    ) -> SemanticMatrixResponse:
        """
        Computes an N x N pairwise similarity matrix across a small collection of texts.
        Bounded to max 10 texts and 20 pairs to prevent quadratic computational explosion.
        """
        start_time = time.perf_counter()
        texts = req.texts
        n = len(texts)
        total_pairs = (n * (n - 1)) // 2

        max_pairs = getattr(quantum_config, "semantic_max_pairs", 20)
        if total_pairs > max_pairs:
            raise SemanticResourceLimitException(
                f"Matrix size ({n} texts = {total_pairs} pairs) exceeds limit ({max_pairs} pairs).",
                details={"num_texts": n, "total_pairs": total_pairs, "max_pairs": max_pairs},
            )

        matrix: List[List[float]] = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        # Precompute features for each text once
        clean_texts = [self.preprocessor.clean_text(t) for t in texts]
        features = [self.feature_extractor.provider.extract_features(t) for t in clean_texts]

        for i in range(n):
            for j in range(i + 1, n):
                pair_req = SemanticAnalysisRequest(
                    text_a=clean_texts[i],
                    text_b=clean_texts[j],
                    method=req.method,
                    framework=req.framework,
                    num_qubits=req.num_qubits,
                    shots=req.shots,
                )
                res = self.analyze_similarity(pair_req, user_id=user_id)
                score = res.similarity_score
                matrix[i][j] = score
                matrix[j][i] = score

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return SemanticMatrixResponse(
            texts=clean_texts,
            matrix=matrix,
            method=req.method or "hybrid",
            num_texts=n,
            total_comparisons=total_pairs,
            execution_time_ms=execution_time_ms,
        )

    def run_benchmark(
        self,
        req: SemanticBenchmarkRequest,
        user_id: Optional[int] = None,
    ) -> SemanticBenchmarkResponse:
        """
        Evaluates classical vs quantum similarity against human-calibrated reference pairs.
        Zero data leakage guaranteed.
        """
        start_time = time.perf_counter()
        adapter = SemanticDatasetAdapter()
        pairs = adapter.load()

        y_true: List[float] = []
        c_preds: List[float] = []
        q_preds: List[float] = []

        c_times: List[float] = []
        q_times: List[float] = []

        for p in pairs:
            y_true.append(p.expected_similarity)

            # Classical
            c_t0 = time.perf_counter()
            c_res = self.analyze_similarity(
                SemanticAnalysisRequest(text_a=p.text_a, text_b=p.text_b, method="classical"),
                user_id=None,
            )
            c_times.append((time.perf_counter() - c_t0) * 1000)
            c_preds.append(c_res.classical_cosine_similarity)

            # Quantum
            q_t0 = time.perf_counter()
            q_res = self.analyze_similarity(
                SemanticAnalysisRequest(
                    text_a=p.text_a,
                    text_b=p.text_b,
                    method="quantum",
                    framework=req.framework,
                    num_qubits=req.num_qubits,
                    shots=req.shots,
                ),
                user_id=None,
            )
            q_times.append((time.perf_counter() - q_t0) * 1000)
            q_preds.append(q_res.quantum_kernel_similarity)

        c_mae, c_rmse, c_pearson, c_spearman = SemanticBenchmarkEvaluator.calculate_metrics(y_true, c_preds)
        q_mae, q_rmse, q_pearson, q_spearman = SemanticBenchmarkEvaluator.calculate_metrics(y_true, q_preds)

        avg_c_lat = float(np.mean(c_times))
        avg_q_lat = float(np.mean(q_times))

        honest_summary = SemanticBenchmarkEvaluator.build_honest_analysis(
            c_mae=c_mae,
            q_mae=q_mae,
            c_pearson=c_pearson,
            q_pearson=q_pearson,
            c_lat=avg_c_lat,
            q_lat=avg_q_lat,
        )

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Persist benchmark experiment
        if self.repo is not None:
            try:
                self.repo.create(
                    experiment_type="quantum_semantic",
                    title=f"Semantic Benchmark Evaluation ({len(pairs)} pairs)",
                    input_payload={"framework": req.framework, "num_qubits": req.num_qubits, "shots": req.shots},
                    results={
                        "classical": {"mae": c_mae, "rmse": c_rmse, "pearson": c_pearson, "latency_ms": avg_c_lat},
                        "quantum": {"mae": q_mae, "rmse": q_rmse, "pearson": q_pearson, "latency_ms": avg_q_lat},
                        "honest_analysis": honest_summary,
                    },
                    user_id=user_id,
                    qubit_count=req.num_qubits,
                    execution_time_ms=execution_time_ms,
                    simulator="qiskit_aer",
                )
            except Exception as e:
                logger.warning(f"Failed to log semantic benchmark experiment: {e}")

        return SemanticBenchmarkResponse(
            dataset_name=adapter.metadata()["dataset_name"],
            sample_count=len(pairs),
            classical_metrics={
                "mae": c_mae,
                "rmse": c_rmse,
                "pearson_correlation": c_pearson,
                "spearman_correlation": c_spearman,
                "average_latency_ms": round(avg_c_lat, 2),
            },
            quantum_metrics={
                "mae": q_mae,
                "rmse": q_rmse,
                "pearson_correlation": q_pearson,
                "spearman_correlation": q_spearman,
                "average_latency_ms": round(avg_q_lat, 2),
            },
            correlation_pearson=q_pearson,
            correlation_spearman=q_spearman,
            mae=q_mae,
            rmse=q_rmse,
            honest_analysis=honest_summary,
            execution_time_ms=execution_time_ms,
        )

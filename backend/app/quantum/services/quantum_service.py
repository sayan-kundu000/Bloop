"""
Bloop Central Quantum Service
Coordinates health checks, framework readiness, execution dispatch,
and experiment persistence.
"""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from backend.app.quantum.config import quantum_config
from backend.app.quantum.laboratory.schemas import (
    CircuitLabRequestSchema,
    GateOperationSchema,
    NoiseModelConfigSchema,
)
from backend.app.quantum.laboratory.service import QuantumLaboratoryService
from backend.app.quantum.services.circuit_service import CircuitService
from backend.app.quantum.services.benchmark_service import BenchmarkService
from backend.app.repositories.quantum_repository import QuantumRepository
from backend.app.schemas.quantum import (
    BenchmarkRequest,
    QuantumBenchmarkResponse,
    QuantumCircuitRequest,
    QuantumCircuitResponse,
    QuantumEmotionRequest,
    QuantumEmotionResponse,
    QuantumSemanticRequest,
    QuantumSemanticResponse,
    QuantumTextRequest,
    QuantumTextResponse,
)
from backend.app.core.logging import logger


from backend.app.quantum.hybrid.service import HybridIntelligenceService


class QuantumService:
    """Central orchestrator for the Bloop Quantum Intelligence Subsystem."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.repo = QuantumRepository(db) if db is not None else None
        self.circuit_service = CircuitService()
        self.lab_service = QuantumLaboratoryService(db)
        self.benchmark_service = BenchmarkService()
        self.hybrid_service = HybridIntelligenceService(db)

    def get_kernel_engine(self, num_qubits: int = 4):
        """Initializes and returns a Qiskit Machine Learning QuantumKernelEngine."""
        from backend.app.quantum.hybrid.kernel import QuantumKernelEngine
        return QuantumKernelEngine(num_qubits=num_qubits)

    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """
        Inspects quantum package availability and execution readiness.
        Guaranteed to not fail or throw exceptions.
        """
        qiskit_ok = False
        aer_ok = False
        pl_ok = False
        pl_qiskit_ok = False
        qml_ok = False

        try:
            import qiskit
            qiskit_ok = True
        except Exception:
            pass

        try:
            import qiskit_aer
            aer_ok = True
        except Exception:
            pass

        try:
            import pennylane
            pl_ok = True
        except Exception:
            pass

        try:
            import pennylane_qiskit
            pl_qiskit_ok = True
        except Exception:
            pass

        try:
            import qiskit_machine_learning
            qml_ok = True
        except Exception:
            pass

        enabled = bool(quantum_config.enabled)
        ready = bool(enabled and qiskit_ok and aer_ok and pl_ok)

        return {
            "enabled": enabled,
            "qiskit_available": qiskit_ok,
            "aer_available": aer_ok,
            "pennylane_available": pl_ok,
            "pennylane_qiskit_available": pl_qiskit_ok,
            "qiskit_machine_learning_available": qml_ok,
            "execution_ready": ready,
            "limits": {
                "max_qubits": quantum_config.max_qubits,
                "max_shots": quantum_config.max_shots,
                "max_execution_time_seconds": quantum_config.max_execution_time,
                "default_shots": quantum_config.default_shots,
            },
        }

    def run_circuit_lab(self, req: QuantumCircuitRequest, user_id: Optional[int] = None) -> QuantumCircuitResponse:
        """Executes a custom circuit request and persists experiment records."""
        gate_schemas = [
            GateOperationSchema(
                gate=op.gate,
                target=op.target,
                control=op.control,
                parameter=op.parameter,
            )
            for op in req.gates
        ]

        noise_cfg = None
        if req.noise:
            noise_cfg = NoiseModelConfigSchema(**req.noise)

        lab_req = CircuitLabRequestSchema(
            num_qubits=req.num_qubits,
            gates=gate_schemas,
            preset=req.preset,
            framework=req.framework or "qiskit",
            shots=req.shots,
            noise_level=req.noise_level,
            noise=noise_cfg,
            noise_profile=req.noise_profile,
            seed=req.seed,
        )
        res = self.lab_service.execute_circuit(lab_req, user_id=user_id)
        return QuantumCircuitResponse(
            num_qubits=res.num_qubits,
            circuit_depth=res.circuit_depth,
            total_gates=res.total_gates,
            counts=res.counts,
            probabilities=res.probabilities,
            state_vector=res.state_vector,
            qasm=res.qasm,
            circuit_diagram_ascii=res.circuit_diagram_ascii,
            is_noisy_simulation=res.is_noisy_simulation,
            execution_time_ms=res.execution_time_ms,
            entropy=res.entropy,
            dominant_state=res.dominant_state,
            noise_model=res.noise_model,
            seed=res.seed,
            framework=res.framework,
            backend=res.backend,
        )

    def run_benchmark(self, req: BenchmarkRequest, user_id: Optional[int] = None) -> QuantumBenchmarkResponse:
        """Executes a multi-category benchmark and persists experiment records."""
        from backend.app.quantum.hybrid.schemas import MultiCategoryBenchmarkRequestSchema
        from backend.app.schemas.quantum import MetricComparison

        cat = getattr(req, "category", "text_classification") or "text_classification"
        seed = getattr(req, "random_seed", 42) or 42
        c_weight = getattr(req, "classical_weight", 0.5) if getattr(req, "classical_weight", None) is not None else 0.5
        q_weight = getattr(req, "quantum_weight", 0.5) if getattr(req, "quantum_weight", None) is not None else 0.5

        bench_req = MultiCategoryBenchmarkRequestSchema(
            category=cat,
            dataset_size=req.dataset_size,
            test_split=req.test_split,
            num_qubits=req.num_qubits,
            shots=req.shots,
            random_seed=seed,
            classical_weight=c_weight,
            quantum_weight=q_weight,
        )
        res = self.hybrid_service.run_benchmark(bench_req, user_id=user_id)

        c_metric = MetricComparison(**res.classical_metrics)
        q_metric = MetricComparison(**res.quantum_metrics)
        h_metric = MetricComparison(**res.hybrid_metrics) if res.hybrid_metrics else None

        return QuantumBenchmarkResponse(
            classical_model=res.classical_model,
            quantum_model=res.quantum_model,
            classical_metrics=c_metric,
            quantum_metrics=q_metric,
            honest_analysis=res.honest_analysis,
            quantum_advantage_detected=res.quantum_advantage_detected,
            summary=res.summary,
            category=res.category,
            dataset=res.dataset,
            hybrid_model=res.hybrid_model,
            hybrid_metrics=h_metric,
            resource_usage=res.resource_usage,
            pipeline_breakdown=res.pipeline_breakdown,
            speech_recommendation=res.speech_recommendation.model_dump() if res.speech_recommendation else None,
        )

    # --------------------------------------------------------------------------
    # Specialized Intelligence Delegations (Foundation for Prompts 23+)
    # --------------------------------------------------------------------------
    def analyze_text(self, req: QuantumTextRequest, user_id: Optional[int] = None) -> QuantumTextResponse:
        from backend.app.quantum.text import QuantumTextService, QuantumTextExperimentRequest

        text_service = QuantumTextService(db=self.db)
        text_req = QuantumTextExperimentRequest(
            text=req.text,
            task=req.task or "classification",
            model=req.model or "hybrid_quantum_classifier",
            framework=req.framework or "qiskit",
            num_qubits=req.num_qubits,
            shots=req.shots,
            circuit_depth=req.circuit_depth or 2,
            category_target=req.category_target,
        )
        res = text_service.analyze_text(text_req, user_id=user_id)
        return QuantumTextResponse(
            input_text=res.input_text,
            tokens=res.tokens,
            classical_features=res.classical_features,
            quantum_probabilities=res.quantum_probabilities,
            predicted_style=res.predicted_style,
            confidence=res.confidence if res.confidence is not None else 0.85,
            classical_baseline_prediction=res.classical_baseline_prediction,
            classical_confidence=res.classical_confidence if res.classical_confidence is not None else 0.85,
            circuit_depth=res.circuit_depth,
            num_qubits=res.num_qubits,
            execution_time_ms=res.execution_time_ms,
            task=res.task,
            model=res.model,
            prediction=res.prediction,
            metrics=res.metrics.model_dump() if res.metrics else None,
            quantum=res.quantum.model_dump() if res.quantum else None,
            pipeline_steps=res.pipeline_steps,
            classical_baseline=res.classical_baseline,
        )


    def analyze_emotion(self, req: QuantumEmotionRequest, user_id: Optional[int] = None) -> QuantumEmotionResponse:
        from backend.app.quantum.emotion import QuantumEmotionService, EmotionExperimentRequest

        emotion_service = QuantumEmotionService(db=self.db)
        emotion_req = EmotionExperimentRequest(
            text=req.text,
            shots=req.shots,
            num_qubits=req.num_qubits or 4,
            circuit_depth=req.circuit_depth or 4,
            framework=req.framework or "pennylane",
            include_recommendation=req.include_recommendation if req.include_recommendation is not None else True,
        )
        res = emotion_service.analyze_emotion(emotion_req, user_id=user_id)
        return QuantumEmotionResponse(
            input_text=res.input_text,
            detected_emotion=res.detected_emotion,
            emotion_scores=res.emotion_scores,
            quantum_probabilities=res.quantum_probabilities,
            hybrid_qnn_confidence=res.hybrid_qnn_confidence if res.hybrid_qnn_confidence is not None else 0.85,
            classical_baseline_emotion=res.classical_baseline_emotion,
            classical_confidence=res.classical_confidence if res.classical_confidence is not None else 0.85,
            entanglement_entropy=res.entanglement_entropy,
            circuit_depth=res.circuit_depth,
            num_qubits=res.num_qubits,
            execution_time_ms=res.execution_time_ms,
            speech_recommendation=res.speech_recommendation.model_dump() if res.speech_recommendation else None,
            metrics=res.metrics,
            classical_baseline=res.classical_baseline,
            quantum=res.quantum,
            pipeline_steps=res.pipeline_steps,
        )

    def analyze_semantics(self, req: QuantumSemanticRequest, user_id: Optional[int] = None) -> QuantumSemanticResponse:
        from backend.app.quantum.semantic import QuantumSemanticService, SemanticAnalysisRequest

        semantic_service = QuantumSemanticService(db=self.db)
        sem_req = SemanticAnalysisRequest(
            text_a=req.text_a,
            text_b=req.text_b,
            method=req.method or "hybrid",
            framework=req.framework or "qiskit",
            num_qubits=req.num_qubits or 4,
            shots=req.shots or 1024,
        )
        res = semantic_service.analyze_similarity(sem_req, user_id=user_id)
        return QuantumSemanticResponse(
            text_a=res.text_a,
            text_b=res.text_b,
            quantum_kernel_similarity=res.quantum_kernel_similarity,
            classical_cosine_similarity=res.classical_cosine_similarity,
            similarity_verdict=res.similarity_verdict,
            divergence=res.divergence,
            num_qubits=res.num_qubits,
            circuit_depth=res.circuit_depth,
            execution_time_ms=res.execution_time_ms,
            method=res.method,
            similarity_score=res.similarity_score,
            classical_similarity=res.classical_similarity,
            quantum_similarity=res.quantum_similarity,
            hybrid_similarity=res.hybrid_similarity,
            semantic_distance=res.semantic_distance,
            feature_dimension=res.feature_dimension,
            reduced_dimension=res.reduced_dimension,
            representation_method=res.representation_method,
            reduction_method=res.reduction_method,
            encoding_method=res.encoding_method,
            quantum_framework=res.quantum_framework,
            quantum_backend=res.quantum_backend,
            shots=res.shots,
            experiment_id=res.experiment_id,
            pipeline_steps=res.pipeline_steps,
        )

    def _safe_persist(self, **kwargs: Any) -> None:
        """Safely logs and persists experiment records without crashing on database error."""
        if self.repo is not None:
            try:
                self.repo.create(**kwargs)
            except Exception as e:
                logger.warning(f"Could not persist quantum experiment log: {e}")

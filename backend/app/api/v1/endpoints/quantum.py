"""
Bloop Quantum Intelligence API Endpoints
Provides quantum text classification, emotion QNN analysis, semantic fidelity,
interactive circuit lab simulation, classical-quantum benchmarking, and subsystem health status.
Protected by user identity, execution rate limits, and resource guards.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_settings
from backend.app.core.config import Settings, settings
from backend.app.core.exceptions import (
    BloopException,
    ErrorCode,
    QuantumDisabledException,
    QuantumExecutionError,
    QubitLimitExceededException,
    ShotLimitExceededException,
)
from backend.app.core.rate_limit import rate_limit
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.repositories.quantum_repository import QuantumRepository
from backend.app.schemas.common import ApiResponse
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
    CircuitComparisonRequest,
    CircuitComparisonResponse,
    CircuitRobustnessRequest,
    CircuitRobustnessResponse,
    TemplateInfoSchema,
    NoiseProfileInfoSchema,
)
from backend.app.quantum.services.quantum_service import QuantumService
from backend.app.quantum.laboratory.service import QuantumLaboratoryService
from backend.app.quantum.hybrid.service import HybridIntelligenceService
from backend.app.quantum.hybrid.schemas import (
    BenchmarkCategoryInfoSchema,
    HybridAnalysisRequestSchema,
    HybridAnalysisResponseSchema,
    SpeechRecommendationRequestSchema,
    SpeechRecommendationSchema,
)

router = APIRouter()


def verify_quantum_enabled(cfg: Settings = Depends(get_settings)):
    """Guardrail: rejects quantum requests with 503 if QUANTUM_ENABLED=false."""
    if not cfg.QUANTUM_ENABLED:
        raise QuantumDisabledException("Quantum intelligence subsystem is disabled in this environment.")


@router.get("/health", response_model=ApiResponse[Dict[str, Any]])
@router.get("/status", response_model=ApiResponse[Dict[str, Any]])
def get_quantum_subsystem_health():
    """
    Returns the real-time operational status, framework availability,
    and computational resource boundaries of the quantum subsystem.
    """
    health_data = QuantumService.get_health_status()
    return ApiResponse(
        success=True,
        data=health_data,
        message="Quantum subsystem health status retrieved successfully.",
    )


@router.post(
    "/circuit",
    response_model=ApiResponse[QuantumCircuitResponse],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def execute_quantum_circuit(
    req: QuantumCircuitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Interactive Quantum Circuit Sandbox: executes arbitrary gate configurations with ideal or noisy Aer simulation.
    Protected: requires authenticated user identity.
    """
    service = QuantumService(db)
    try:
        res = service.run_circuit_lab(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Quantum circuit simulated successfully.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))


@router.post(
    "/circuit/compare",
    response_model=ApiResponse[CircuitComparisonResponse],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def compare_quantum_circuits(
    req: CircuitComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mode C: Comparative Experiment between ideal and noisy execution.
    Calculates TVD, Classical Fidelity, and state-by-state divergence.
    Protected: requires authenticated user identity.
    """
    lab_service = QuantumLaboratoryService(db)
    try:
        res = lab_service.compare_circuits(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Circuit comparison completed successfully.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))


@router.post(
    "/circuit/robustness",
    response_model=ApiResponse[CircuitRobustnessResponse],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def run_circuit_robustness(
    req: CircuitRobustnessRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mode D: Robustness Experiment across a bounded parameter sweep.
    Tracks fidelity decay, TVD progression, and target-state survival probability.
    Protected: requires authenticated user identity.
    """
    lab_service = QuantumLaboratoryService(db)
    try:
        res = lab_service.run_robustness(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Circuit robustness experiment completed successfully.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))


@router.get("/circuit/templates", response_model=ApiResponse[List[TemplateInfoSchema]])
def get_circuit_templates():
    """
    Returns available deterministic circuit templates with analytical support expectations.
    """
    templates = QuantumLaboratoryService.list_templates()
    return ApiResponse(success=True, data=templates, message="Circuit templates retrieved successfully.")


@router.get("/circuit/noise-profiles", response_model=ApiResponse[List[NoiseProfileInfoSchema]])
def get_noise_profiles():
    """
    Returns available preset noise profiles (IDEAL, LOW, MEDIUM, HIGH).
    """
    profiles = QuantumLaboratoryService.list_noise_profiles()
    return ApiResponse(success=True, data=profiles, message="Noise profiles retrieved successfully.")


@router.get("/circuit/gates", response_model=ApiResponse[List[Dict[str, Any]]])
def get_supported_circuit_gates():
    """
    Returns the supported quantum gate whitelist, arity, and parameter specifications.
    """
    gates = QuantumLaboratoryService.get_supported_gates()
    return ApiResponse(success=True, data=gates, message="Supported gate whitelist retrieved successfully.")


@router.post(
    "/benchmark",
    response_model=ApiResponse[QuantumBenchmarkResponse],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def run_quantum_benchmark(
    req: BenchmarkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Empirical benchmark comparing classical ML (Logistic Regression) vs Quantum Classifier (VQC).
    Protected: requires authenticated user identity.
    """
    service = QuantumService(db)
    try:
        res = service.run_benchmark(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Benchmark evaluation completed.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))


@router.get(
    "/benchmark/categories",
    response_model=ApiResponse[List[BenchmarkCategoryInfoSchema]],
)
def get_benchmark_categories():
    """
    Returns supported benchmark categories, descriptions, baseline/candidate pairs, and metrics.
    """
    categories = HybridIntelligenceService.get_supported_categories()
    return ApiResponse(
        success=True,
        data=categories,
        message="Supported benchmark categories retrieved successfully.",
    )


@router.post(
    "/hybrid/analyze",
    response_model=ApiResponse[HybridAnalysisResponseSchema],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def analyze_hybrid_intelligence(
    req: HybridAnalysisRequestSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Executes hybrid intelligence analysis combining classical baseline and quantum state-space representations.
    Derives optional provider-independent acoustic speech recommendations.
    Protected: requires authenticated user identity.
    """
    service = HybridIntelligenceService(db)
    try:
        res = service.analyze_hybrid(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Hybrid intelligence analysis completed.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))


@router.post(
    "/hybrid/recommend",
    response_model=ApiResponse[SpeechRecommendationSchema],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def generate_speech_recommendation(
    req: SpeechRecommendationRequestSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Derives auditable, provider-independent acoustic speech recommendations with voice capability validation.
    Protected: requires authenticated user identity.
    """
    service = HybridIntelligenceService(db)
    try:
        res = service.generate_recommendation(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Speech recommendation generated successfully.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))


@router.post(
    "/text",
    response_model=ApiResponse[QuantumTextResponse],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def quantum_text_analysis(
    req: QuantumTextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyzes text style and sentiment using quantum angle encoding and a Variational Quantum Classifier (VQC).
    Protected: requires authenticated user identity.
    """
    service = QuantumService(db)
    try:
        res = service.analyze_text(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Quantum text classification complete.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))


@router.post(
    "/emotion",
    response_model=ApiResponse[QuantumEmotionResponse],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def quantum_emotion_analysis(
    req: QuantumEmotionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyzes multi-class affective tone using a PennyLane Hybrid Quantum Neural Network and entanglement metrics.
    Protected: requires authenticated user identity.
    """
    service = QuantumService(db)
    try:
        res = service.analyze_emotion(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Quantum emotion analysis complete.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))


from backend.app.quantum.semantic import (
    SemanticBenchmarkRequest,
    SemanticBenchmarkResponse,
    SemanticMatrixRequest,
    SemanticMatrixResponse,
)


@router.post(
    "/semantic",
    response_model=ApiResponse[QuantumSemanticResponse],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def quantum_semantic_similarity(
    req: QuantumSemanticRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Computes Quantum Kernel State Fidelity between two text prompts to measure semantic similarity.
    Protected: requires authenticated user identity.
    """
    service = QuantumService(db)
    try:
        res = service.analyze_semantics(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Quantum semantic similarity computed.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))


@router.post(
    "/semantic/matrix",
    response_model=ApiResponse[SemanticMatrixResponse],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def quantum_semantic_matrix(
    req: SemanticMatrixRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Computes pairwise semantic similarity matrix across a collection of texts (max 10 texts / 20 pairs).
    Protected: requires authenticated user identity.
    """
    from backend.app.quantum.semantic import QuantumSemanticService
    service = QuantumSemanticService(db)
    try:
        res = service.compute_matrix(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Semantic similarity matrix computed.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))


@router.post(
    "/semantic/benchmark",
    response_model=ApiResponse[SemanticBenchmarkResponse],
    dependencies=[
        Depends(verify_quantum_enabled),
        Depends(rate_limit(requests_per_minute=settings.RATE_LIMIT_PER_MINUTE_QUANTUM)),
    ],
)
def quantum_semantic_benchmark(
    req: SemanticBenchmarkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Executes classical vs quantum semantic similarity benchmark across reference benchmark pairs.
    Protected: requires authenticated user identity.
    """
    from backend.app.quantum.semantic import QuantumSemanticService
    service = QuantumSemanticService(db)
    try:
        res = service.run_benchmark(req, user_id=current_user.id)
        return ApiResponse(success=True, data=res, message="Semantic benchmark evaluation completed.")
    except BloopException as be:
        raise be
    except Exception as e:
        raise QuantumExecutionError(str(e))



@router.get("/history", response_model=ApiResponse[List[dict]])
def get_quantum_history(
    experiment_type: Optional[str] = Query(None, description="Filter by experiment type (text, emotion, semantic, circuit, benchmark)"),
    limit: int = Query(20, ge=1, le=50, description="Max records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves recent quantum intelligence experiment logs and benchmark metrics.
    Protected: requires authenticated user identity.
    """
    repo = QuantumRepository(db)
    items = repo.list_recent(user_id=current_user.id, experiment_type=experiment_type, limit=limit)
    return ApiResponse(
        success=True,
        data=[
            {
                "id": exp.id,
                "type": exp.experiment_type,
                "title": exp.title,
                "qubit_count": exp.qubit_count,
                "circuit_depth": exp.circuit_depth,
                "execution_time_ms": exp.execution_time_ms,
                "created_at": exp.created_at.isoformat(),
            }
            for exp in items
        ],
        message="Quantum experiment history retrieved."
    )


@router.get("/history/{experiment_id}", response_model=ApiResponse[dict])
def get_quantum_experiment_detail(
    experiment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves full details of a specific quantum experiment owned by the authenticated user.
    Protected: requires authenticated user identity and ownership.
    """
    repo = QuantumRepository(db)
    exp = repo.get_by_id(experiment_id=experiment_id, user_id=current_user.id)
    if not exp:
        from backend.app.core.exceptions import ResourceNotFoundException
        raise ResourceNotFoundException(resource="QuantumExperiment", identifier=experiment_id)

    return ApiResponse(
        success=True,
        data={
            "id": exp.id,
            "type": exp.experiment_type,
            "title": exp.title,
            "description": exp.description,
            "status": exp.status,
            "qubit_count": exp.qubit_count,
            "circuit_depth": exp.circuit_depth,
            "execution_time_ms": exp.execution_time_ms,
            "simulator": exp.simulator,
            "input_payload": exp.input_payload,
            "results": exp.results,
            "created_at": exp.created_at.isoformat(),
        },
        message="Quantum experiment details retrieved."
    )

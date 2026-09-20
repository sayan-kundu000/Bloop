"""
Bloop Health & Readiness Endpoints
Provides system liveness, readiness, and subsystem diagnostic probes.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.schemas.common import ApiResponse

router = APIRouter()


@router.get("/health", response_model=ApiResponse[Dict[str, Any]])
def check_health(db: Session = Depends(get_db)):
    """
    Comprehensive subsystem health check for monitoring dashboards and deployment pipelines.
    Reports database connectivity, ElevenLabs provider readiness, and quantum subsystem availability.
    """
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return ApiResponse(
        success=(db_status == "healthy"),
        data={
            "status": "healthy" if db_status == "healthy" else "degraded",
            "database": db_status,
            "provider": "configured" if bool(settings.ELEVENLABS_API_KEY.strip()) else "unconfigured",
            "quantum": "available" if settings.QUANTUM_ENABLED else "disabled",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
        },
        message="Bloop service is operational." if db_status == "healthy" else "Bloop service is degraded."
    )


@router.get("/health/live", response_model=ApiResponse[Dict[str, str]])
def check_liveness():
    """
    Liveness probe for process supervisors and container orchestrators.
    Answers: Is the application process running and capable of responding to HTTP?
    """
    return ApiResponse(
        success=True,
        data={"status": "alive"},
        message="Application process is alive."
    )


@router.get("/health/ready")
def check_readiness(db: Session = Depends(get_db)):
    """
    Readiness probe for load balancers and reverse proxies (e.g. Render).
    Answers: Can this instance currently serve API traffic and interact with its database?
    """
    try:
        db.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "data": {
                    "status": "ready",
                    "database": "connected",
                },
                "message": "Application is ready to receive traffic.",
            },
        )
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_UNAVAILABLE",
                    "message": "Database readiness probe failed.",
                    "details": {"error": "Connection error"},
                },
            },
        )

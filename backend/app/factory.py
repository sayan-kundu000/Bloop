"""
Bloop Application Factory Module
Provides a clean, testable create_app() factory function that assembles
FastAPI metadata, lifespan, middleware, exception handlers, and versioned routing.
"""

from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI
from sqlalchemy import text

from backend.app.api.router import api_router
from backend.app.core.config import Settings, settings as global_settings
from backend.app.core.exceptions import register_exception_handlers
from backend.app.core.http_client import close_http_client, init_http_client
from backend.app.core.logging import logger, setup_logging
from backend.app.core.middleware import register_middleware
from backend.app.db.init_db import init_db
from backend.app.db.session import SessionLocal, engine
from backend.app.services.voice_service import VoiceService

# OpenAPI Tag Metadata
OPENAPI_TAGS = [
    {
        "name": "Health",
        "description": "System liveness, readiness, and operational probes for infrastructure monitoring.",
    },
    {
        "name": "Authentication",
        "description": "User registration, credential authentication, and JWT access token issuance.",
    },
    {
        "name": "Users",
        "description": "User identity, profiles, and personalization preferences.",
    },
    {
        "name": "Languages",
        "description": "Supported language catalog and locale configurations.",
    },
    {
        "name": "Voices",
        "description": "Dynamic voice registry, provider discovery, and voice attributes.",
    },
    {
        "name": "Speech",
        "description": "Text-to-speech synthesis, streaming audio, and acoustic modulation.",
    },
    {
        "name": "History",
        "description": "Audio generation audit trail and audio lifecycle management.",
    },
    {
        "name": "Favorites",
        "description": "User-curated speech generation bookmarks and library management.",
    },
    {
        "name": "Quantum",
        "description": "Quantum-enhanced emotion modeling, QNN simulations, and parameter modulation.",
    },
]


def create_app(custom_settings: Optional[Settings] = None) -> FastAPI:
    """
    Application Factory for Bloop AI Platform.
    Assembles FastAPI instance with environment-aware configuration,
    ordered middleware pipeline, centralized error handlers, and versioned routes.
    """
    cfg = custom_settings or global_settings

    # Ensure structured logging is initialized
    setup_logging()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # --------------------------------------------------------------------
        # Startup Phase: Non-destructive resource checks & HTTP client init
        # --------------------------------------------------------------------
        logger.info(f"Starting {cfg.APP_NAME} [version={cfg.APP_VERSION}, env={cfg.APP_ENV}]...")
        
        # Verify database connectivity safely and initialize tables
        db = SessionLocal()
        try:
            init_db(db)
            # In development/test environments, import voice config if present
            if cfg.APP_ENV != "production":
                voice_service = VoiceService(db)
                voice_service.import_voices_from_config()
        except Exception as exc:
            logger.warning(f"Startup database initialization notice: {exc}")
        finally:
            db.close()

        # Initialize managed HTTP client session
        app.state.http_client = await init_http_client()
        app.state.settings = cfg
        logger.info("Application startup complete. Ready to serve requests.")

        yield

        # --------------------------------------------------------------------
        # Shutdown Phase: Clean resource release
        # --------------------------------------------------------------------
        logger.info(f"Shutting down {cfg.APP_NAME}...")
        await close_http_client()
        engine.dispose()
        logger.info("Engine connections disposed. Shutdown complete.")

    # Instantiate FastAPI with environment-aware documentation toggling
    app = FastAPI(
        title="Bloop AI Text-to-Speech & Quantum Intelligence API",
        description="Intermediate-level AI Speech Synthesis and Quantum Intelligence experimentation platform.",
        version=cfg.APP_VERSION,
        docs_url="/docs" if cfg.APP_DEBUG else None,
        redoc_url="/redoc" if cfg.APP_DEBUG else None,
        openapi_url=f"{cfg.API_V1_PREFIX}/openapi.json" if cfg.APP_DEBUG else None,
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
    )
    app.state.settings = cfg

    # 1. Register middleware pipeline (CORS, RequestID, SecurityHeaders, Timing, PayloadLimit)
    register_middleware(app, cfg)

    # 2. Register centralized exception handlers (BloopException, HTTP, Validation, SQLAlchemy)
    register_exception_handlers(app)

    # 3. Mount versioned API routes under configured prefix (default: /api/v1)
    app.include_router(api_router, prefix=cfg.API_V1_PREFIX)

    # 4. Mount Root probe endpoint
    @app.get("/", tags=["Health"])
    def root():
        """Root API metadata endpoint."""
        return {
            "app": cfg.APP_NAME,
            "version": cfg.APP_VERSION,
            "status": "online",
            "docs": "/docs" if cfg.APP_DEBUG else "disabled_in_production",
            "api_v1": cfg.API_V1_PREFIX,
        }

    return app

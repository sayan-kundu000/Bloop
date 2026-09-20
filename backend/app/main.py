"""
Bloop FastAPI Application Entry Point
Exports the application instance assembled by create_app().
Supports Render $PORT dynamic binding and local development reload.
"""

import os
from backend.app.core.config import settings
from backend.app.factory import create_app

# Assemble FastAPI application instance via application factory
app = create_app()

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.APP_DEBUG,
    )

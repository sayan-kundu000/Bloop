"""
Database FastAPI Dependencies
Provides request-scoped database sessions for routes and controllers.
"""

from backend.app.db.session import get_db

__all__ = ["get_db"]

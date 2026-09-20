"""
Integration Tests — Database Persistence & Multi-Tenant Boundaries
"""

import pytest
from backend.app.db.session import SessionLocal
from backend.app.models.user import User


def test_database_session_can_query():
    db = SessionLocal()
    try:
        # Verify active connection and query execution
        users = db.query(User).limit(5).all()
        assert isinstance(users, list)
    finally:
        db.close()

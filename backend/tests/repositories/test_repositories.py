"""
Repository Tests — User and Persistence Verification
"""

import pytest
from backend.app.repositories.user_repository import UserRepository
from backend.app.db.session import SessionLocal


def test_user_repository_lookup():
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        # Verify query method executes cleanly against test session
        user = repo.get_by_id(99999)
        assert user is None
    finally:
        db.close()

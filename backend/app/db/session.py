"""
Bloop SQLAlchemy 2.x Session Management & Connection Pooling
Configures connection engine parameters optimized for Render PostgreSQL
with seamless local SQLite fallback, and yields request-scoped sessions.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.db.base import Base

# Engine configuration based on database dialect
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
        echo=False,
    )
else:
    # PostgreSQL configuration tuned for Render Managed Database
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
    )

# Session factory for generating request-scoped database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a request-scoped database session.
    Automatically rolls back uncommitted transactions if an error occurs,
    and guarantees that the session connection is returned to the pool.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
]

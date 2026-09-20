"""
Bloop SQLAlchemy 2.x Declarative Base & Model Registry
Defines the authoritative DeclarativeBase with standard constraint naming conventions
and registers all application domain models for Alembic discovery.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# PostgreSQL-friendly standardized constraint naming convention
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Modern SQLAlchemy 2.x Declarative Base with naming conventions."""
    metadata = MetaData(naming_convention=convention)


# Register models for Alembic and Base.metadata discovery
# (Imports occur after Base definition to prevent circular imports)
def _register_models():
    from backend.app.models.user import User  # noqa: F401
    from backend.app.models.user_preference import UserPreference  # noqa: F401
    from backend.app.models.language import Language  # noqa: F401
    from backend.app.models.voice import Voice  # noqa: F401
    from backend.app.models.speech_generation import SpeechGeneration  # noqa: F401
    from backend.app.models.favorite import Favorite  # noqa: F401
    from backend.app.models.quantum_experiment import QuantumExperiment  # noqa: F401


_register_models()

__all__ = ["Base"]

"""
Bloop User Domain Model (SQLAlchemy 2.x)
Represents registered user identity, credentials, and top-level entity relationships.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.user_preference import UserPreference
    from backend.app.models.speech_generation import SpeechGeneration
    from backend.app.models.favorite import Favorite
    from backend.app.models.quantum_experiment import QuantumExperiment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    preference: Mapped[Optional["UserPreference"]] = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    generations: Mapped[List["SpeechGeneration"]] = relationship(
        "SpeechGeneration",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    experiments: Mapped[List["QuantumExperiment"]] = relationship(
        "QuantumExperiment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email!r}, is_active={self.is_active})>"

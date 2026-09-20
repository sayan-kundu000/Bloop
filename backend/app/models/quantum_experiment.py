"""
Bloop Quantum Experiment Domain Model (SQLAlchemy 2.x)
Represents quantum simulation executions, benchmarks, circuit logs, and metadata.
Strictly decoupled from core TTS synthesis.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.user import User


class QuantumExperiment(Base):
    __tablename__ = "quantum_experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    experiment_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="completed", nullable=False, index=True)
    input_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    results: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    qubit_count: Mapped[Optional[int]] = mapped_column(Integer, default=2, nullable=True)
    circuit_depth: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    execution_time_ms: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    simulator: Mapped[Optional[str]] = mapped_column(String(50), default="qiskit_aer", nullable=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="experiments")

    __table_args__ = (
        Index("ix_quantum_experiments_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<QuantumExperiment(id={self.id}, type={self.experiment_type!r}, "
            f"user_id={self.user_id}, status={self.status!r})>"
        )

"""
Bloop Favorite Domain Model (SQLAlchemy 2.x)
Represents bookmarked speech generations associated with specific users.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.speech_generation import SpeechGeneration


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    generation_id: Mapped[int] = mapped_column(
        ForeignKey("speech_generations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    generation: Mapped["SpeechGeneration"] = relationship("SpeechGeneration", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("user_id", "generation_id", name="uq_user_generation_favorite"),
    )

    def __repr__(self) -> str:
        return f"<Favorite(id={self.id}, user_id={self.user_id}, generation_id={self.generation_id})>"

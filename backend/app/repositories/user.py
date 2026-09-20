"""
Bloop User Repository (SQLAlchemy 2.x)
Encapsulates data persistence and queries for the User domain.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.user_preference import UserPreference
from backend.app.schemas.user import UserCreate, UserUpdate
from backend.app.services.auth.password import hash_password as get_password_hash


class UserRepository:
    """Repository handling persistence and queries for the User identity domain."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        clean_email = email.lower().strip()
        stmt = select(User).where(User.email == clean_email)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, user_in: UserCreate) -> User:
        clean_email = user_in.email.lower().strip()
        user = User(
            email=clean_email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Create default preferences record
        pref = UserPreference(user_id=user.id)
        self.db.add(pref)
        self.db.commit()

        return user

    def update_profile(self, user: User, full_name: Optional[str]) -> User:
        """
        Safely update permitted profile attributes (full_name) transactionally.
        Excludes passwords, emails, superuser status, and immutable identifiers (Prompt 15 §8).
        """
        user.full_name = full_name.strip() if full_name and full_name.strip() else None
        self.db.commit()
        self.db.refresh(user)
        return user


    def update(self, user: User, user_in: UserUpdate) -> User:
        if user_in.full_name is not None:
            clean_name = user_in.full_name.strip() if user_in.full_name.strip() else None
            user.full_name = clean_name
        if hasattr(user_in, "password") and user_in.password:
            user.hashed_password = get_password_hash(user_in.password)
        self.db.commit()
        self.db.refresh(user)
        return user


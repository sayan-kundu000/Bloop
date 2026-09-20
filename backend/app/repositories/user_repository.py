"""
Bloop User Repository Alias
Re-exports UserRepository from backend.app.repositories.user for backward compatibility.
"""

from backend.app.repositories.user import UserRepository

__all__ = ["UserRepository"]

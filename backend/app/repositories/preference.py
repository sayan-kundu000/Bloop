"""
Bloop Preference Repository Module Alias
Re-exports UserPreferenceRepository as PreferenceRepository.
"""

from backend.app.repositories.user_preference import UserPreferenceRepository

PreferenceRepository = UserPreferenceRepository

__all__ = ["PreferenceRepository", "UserPreferenceRepository"]

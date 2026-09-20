"""
Bloop Preference Repository Legacy Alias
Re-exports UserPreferenceRepository as PreferenceRepository for backward compatibility.
"""

from backend.app.repositories.user_preference import UserPreferenceRepository

# Alias
PreferenceRepository = UserPreferenceRepository

__all__ = ["PreferenceRepository", "UserPreferenceRepository"]

"""
Bloop User Preference Legacy Import Alias
Re-exports UserPreference from backend.app.models.user_preference for backward compatibility.
"""

from backend.app.models.user_preference import UserPreference

__all__ = ["UserPreference"]

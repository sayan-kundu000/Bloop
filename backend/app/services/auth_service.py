"""
Bloop Authentication Service Alias Module
Maintains backward compatibility by re-exporting AuthService from backend.app.services.auth.
"""

from backend.app.services.auth.service import AuthService

__all__ = ["AuthService"]

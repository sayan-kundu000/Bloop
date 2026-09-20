"""
Bloop Favorite Repository Legacy Alias
Re-exports FavoriteRepository from backend.app.repositories.favorite for backward compatibility.
"""

from backend.app.repositories.favorite import FavoriteRepository

__all__ = ["FavoriteRepository"]

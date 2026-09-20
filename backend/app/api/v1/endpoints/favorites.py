"""
Bloop Favorite Endpoints
Provides bookmarking, listing, and deletion of favorite speech generation outputs.
Thin router delegating business logic to FavoriteService (Prompt 16 §51).
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.common import ApiResponse, PaginatedResponse, PaginationMeta
from backend.app.schemas.favorite import (
    FavoriteCreate,
    FavoriteDeleteResponse,
    FavoriteResponse,
)
from backend.app.services.favorites.service import FavoriteService

router = APIRouter()


@router.get("", response_model=ApiResponse[PaginatedResponse[FavoriteResponse]])
def get_favorites(
    search: Optional[str] = Query(None, description="Search favorites by text, voice name, or label"),
    language: Optional[str] = Query(None, description="Filter favorites by language code"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve user-curated favorite speech generations with search, filtering, and pagination.
    Strictly scoped to the requesting authenticated user.
    """
    fav_service = FavoriteService(db)
    items, total = fav_service.list_favorites(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search,
        language=language,
    )

    has_next = (page * page_size) < total
    has_prev = page > 1
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return ApiResponse(
        success=True,
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
            has_prev=has_prev,
            total_pages=total_pages,
        ),
        meta=PaginationMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        ),
        message="Favorites retrieved successfully."
    )


@router.post("", response_model=ApiResponse[FavoriteResponse], status_code=status.HTTP_201_CREATED)
def add_favorite(
    fav_in: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Bookmarks a speech generation record. Enforces existence, user ownership, and duplicate conflict checks.
    """
    fav_service = FavoriteService(db)
    fav_res = fav_service.add_favorite(
        user_id=current_user.id,
        generation_id=fav_in.generation_id,
        label=fav_in.label,
    )

    return ApiResponse(
        success=True,
        data=fav_res,
        message="Added to favorites successfully.",
    )


@router.delete("/generation/{generation_id}", response_model=ApiResponse[FavoriteDeleteResponse])
def remove_favorite_by_generation(
    generation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Convenience endpoint: removes a bookmark by target speech generation ID.
    """
    fav_service = FavoriteService(db)
    deleted_id = fav_service.remove_favorite_by_generation(
        user_id=current_user.id,
        generation_id=generation_id,
    )

    return ApiResponse(
        success=True,
        data=FavoriteDeleteResponse(deleted_id=deleted_id, message="Favorite removed."),
        message="Removed from favorites successfully.",
    )


@router.delete("/{favorite_id}", response_model=ApiResponse[FavoriteDeleteResponse])
def remove_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Removes a bookmarked favorite with resource ownership validation.
    """
    fav_service = FavoriteService(db)
    deleted_id = fav_service.remove_favorite(
        favorite_id=favorite_id,
        user=current_user,
    )

    return ApiResponse(
        success=True,
        data=FavoriteDeleteResponse(deleted_id=deleted_id, message="Favorite removed."),
        message="Removed from favorites successfully.",
    )

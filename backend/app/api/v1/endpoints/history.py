"""
Bloop Speech Generation History Endpoints
Provides paginated query, search, filtering, retrieval, and deletion of speech generation records.
Strictly scoped to the authenticated requesting user's identity (Prompt 14 §39 & Prompt 15 §20-26).
Thin router delegating business logic to HistoryService (Prompt 15 §33).
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.common import ApiResponse, PaginatedResponse, PaginationMeta
from backend.app.schemas.history import HistoryItemResponse, HistoryQueryFilter
from backend.app.services.history.service import HistoryService
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

router = APIRouter()


@router.get("", response_model=ApiResponse[PaginatedResponse[HistoryItemResponse]])
def get_history(
    search: Optional[str] = Query(None, description="Search text content or voice name"),
    language: Optional[str] = Query(None, description="Filter by language code (e.g. en-US)"),
    status: Optional[str] = Query(None, pattern="^(completed|failed|pending|processing)$", description="Filter by status"),
    favorite: Optional[bool] = Query(None, description="Filter favorited generations only if true, non-favorited if false"),
    created_after: Optional[datetime] = Query(None, description="Filter generations created on or after ISO timestamp"),
    created_before: Optional[datetime] = Query(None, description="Filter generations created on or before ISO timestamp"),
    sort_by: str = Query("created_at", pattern="^(created_at|duration_seconds|char_count|word_count)$", description="Sort attribute"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve speech generation history with filtering, search, sorting, and pagination.
    Protected: strictly scopes results exclusively to the authenticated user's records.
    """
    filter_params = HistoryQueryFilter(
        search=search,
        language=language,
        status=status,
        favorite=favorite,
        created_after=created_after,
        created_before=created_before,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )

    history_service = HistoryService(db)
    items, total = history_service.list_history(current_user.id, filter_params)

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
        message="History retrieved successfully."
    )


@router.get("/{generation_id}", response_model=ApiResponse[HistoryItemResponse])
def get_generation_by_id(
    generation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a single speech generation record by ID with resource ownership enforcement.
    Returns HTTP 403 if the record belongs to another user (Prompt 15 §25).
    """
    history_service = HistoryService(db)
    item = history_service.get_generation_detail(generation_id, current_user)

    return ApiResponse(
        success=True,
        data=item,
        message="Speech generation record retrieved."
    )


@router.delete("/{generation_id}", response_model=ApiResponse[dict])
def delete_generation(
    generation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a speech generation record and purge its associated audio file.
    Enforces resource ownership. Returns HTTP 403 if belonging to another user (Prompt 15 §26).
    """
    history_service = HistoryService(db)
    history_service.delete_generation(generation_id, current_user)

    return ApiResponse(
        success=True,
        data={"deleted_id": generation_id},
        message="Generation deleted successfully."
    )

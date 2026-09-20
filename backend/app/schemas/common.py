"""
Bloop Common Schema Definitions
Standardized API envelopes, pagination containers, error structures, and query parameters.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Structured error descriptor returning machine-readable code, message, and diagnostic context."""
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable descriptive error message")
    details: Optional[Any] = Field(default_factory=dict, description="Field-specific errors or additional details")


class PaginationMeta(BaseModel):
    """Structured pagination metadata returned in list collection responses."""
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total: int = Field(..., ge=0, description="Total number of items matching query")
    total_pages: int = Field(..., ge=0, description="Total number of pages available")
    has_next: bool = Field(..., description="Whether a next page exists")
    has_prev: bool = Field(False, description="Whether a previous page exists")


class ApiResponse(BaseModel, Generic[T]):
    """
    Standardized API response envelope used across all Bloop endpoints.
    Follows: { success: bool, data?: T, error?: ErrorDetail, message?: str, meta?: dict }
    """
    success: bool = Field(True, description="Indicates if the operation succeeded")
    data: Optional[T] = Field(None, description="Response payload data")
    error: Optional[ErrorDetail] = Field(None, description="Error details when success is False")
    message: Optional[str] = Field(None, description="Human-readable operational message")
    meta: Optional[Union[Dict[str, Any], PaginationMeta]] = Field(None, description="Collection pagination or metadata")


class PaginatedResponse(BaseModel, Generic[T]):
    """Container for paginated collections."""
    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total count across all pages")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items requested per page")
    has_next: bool = Field(..., description="True if next page exists")
    has_prev: bool = Field(False, description="True if previous page exists")
    total_pages: Optional[int] = Field(None, description="Total calculated pages")

    def __init__(self, **data):
        super().__init__(**data)
        if self.total_pages is None and self.page_size > 0:
            import math
            self.total_pages = math.ceil(self.total / self.page_size) if self.total > 0 else 1
        if not self.has_prev:
            self.has_prev = self.page > 1

"""Common API Schemas, Pagination, Sorting, and Response Wrappers.

Provides standardized query parameters and unified JSON response envelopes across the API.
"""

from math import ceil
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Standardized query parameters for paginated list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number starting from 1")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")

    @property
    def offset(self) -> int:
        """Calculate database query offset."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Calculate database query limit."""
        return self.page_size


class SortParams(BaseModel):
    """Standardized sorting parameters."""

    sort_by: str = Field(default="created_at", description="Field name to sort by")
    order: Literal["asc", "desc"] = Field(default="desc", description="Sort direction: asc or desc")


class PaginationMeta(BaseModel):
    """Pagination metadata included in paginated responses."""

    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items requested per page")
    total_items: int = Field(..., description="Total matching items across all pages")
    total_pages: int = Field(..., description="Total available pages")
    has_next: bool = Field(..., description="Whether a next page exists")
    has_prev: bool = Field(..., description="Whether a previous page exists")

    @classmethod
    def create(cls, page: int, page_size: int, total_items: int) -> "PaginationMeta":
        """Compute pagination metadata dynamically."""
        total_pages = max(1, ceil(total_items / page_size)) if total_items > 0 else 1
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


class DataResponse(BaseModel, Generic[T]):
    """Unified single-resource response envelope."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: T = Field(..., description="Resource payload")
    meta: dict[str, Any] | None = Field(default=None, description="Optional metadata")


class PaginatedResponse(BaseModel, Generic[T]):
    """Unified collection list response envelope with pagination."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: list[T] = Field(..., description="List of items for current page")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")

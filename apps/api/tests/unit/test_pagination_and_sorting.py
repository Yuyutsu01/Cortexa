"""Unit Tests for Pagination, Sorting, and Meta Calculations."""

import pytest
from pydantic import ValidationError

from app.schemas.common import PaginationMeta, PaginationParams, SortParams


def test_pagination_params_offset_and_limit() -> None:
    """Verify offset and limit calculations across various pages."""
    p1 = PaginationParams(page=1, page_size=20)
    assert p1.offset == 0
    assert p1.limit == 20

    p2 = PaginationParams(page=3, page_size=15)
    assert p2.offset == 30
    assert p2.limit == 15


def test_pagination_params_validation_bounds() -> None:
    """Verify bounds enforcement on page and page_size."""
    with pytest.raises(ValidationError):
        PaginationParams(page=0, page_size=20)

    with pytest.raises(ValidationError):
        PaginationParams(page=1, page_size=101)


def test_pagination_meta_calculations() -> None:
    """Verify page count, has_next, and has_prev calculations."""
    meta = PaginationMeta.create(page=1, page_size=10, total_items=25)
    assert meta.page == 1
    assert meta.total_items == 25
    assert meta.total_pages == 3
    assert meta.has_next is True
    assert meta.has_prev is False

    last_meta = PaginationMeta.create(page=3, page_size=10, total_items=25)
    assert last_meta.has_next is False
    assert last_meta.has_prev is True

    empty_meta = PaginationMeta.create(page=1, page_size=20, total_items=0)
    assert empty_meta.total_pages == 1
    assert empty_meta.has_next is False
    assert empty_meta.has_prev is False


def test_sort_params_defaults() -> None:
    """Verify sort parameter parsing and defaults."""
    sort = SortParams()
    assert sort.sort_by == "created_at"
    assert sort.order == "desc"

    custom_sort = SortParams(sort_by="email", order="asc")
    assert custom_sort.sort_by == "email"
    assert custom_sort.order == "asc"

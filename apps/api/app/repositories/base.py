"""Base Repository & Tenant-Aware Repository Abstractions.

Provides reusable, type-safe data access patterns, pagination, dynamic sorting,
and strict tenant isolation.
"""

from collections.abc import Sequence
from datetime import UTC
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseEntity, SoftDeleteMixin, TenantAwareEntity
from app.schemas.common import PaginationParams, SortParams

ModelType = TypeVar("ModelType", bound=BaseEntity)
TenantModelType = TypeVar("TenantModelType", bound=TenantAwareEntity)


class BaseRepository(Generic[ModelType]):
    """Generic repository handling data access for persistent entities."""

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    def _apply_soft_delete_filter(self, query: Any, include_deleted: bool = False) -> Any:
        """Filter out soft-deleted records unless explicitly requested."""
        if not include_deleted and issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.is_deleted == False)  # noqa: E712
        return query

    def _apply_sorting(self, query: Any, sort: SortParams | None = None) -> Any:
        """Apply parameterized sorting to prevent raw SQL injection."""
        if sort is None:
            if hasattr(self.model, "created_at"):
                return query.order_by(self.model.created_at.desc())
            return query.order_by(self.model.id.desc())

        sort_attr = getattr(self.model, sort.sort_by, None)
        sort_column = (
            sort_attr if sort_attr is not None else getattr(self.model, "created_at", self.model.id)
        )

        if sort.order.lower() == "asc":
            return query.order_by(sort_column.asc())
        return query.order_by(sort_column.desc())

    async def get_by_id(self, id: UUID, include_deleted: bool = False) -> ModelType | None:
        """Retrieve a single entity by its primary key UUID."""
        query = select(self.model).where(self.model.id == id)
        query = self._apply_soft_delete_filter(query, include_deleted)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list(
        self,
        pagination: PaginationParams,
        sort: SortParams | None = None,
        include_deleted: bool = False,
    ) -> tuple[Sequence[ModelType], int]:
        """List entities with pagination and return total matching count."""
        # 1. Base query with soft delete filter
        base_query = select(self.model)
        base_query = self._apply_soft_delete_filter(base_query, include_deleted)

        # 2. Count total records
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()

        # 3. Apply sorting and pagination offsets
        paginated_query = self._apply_sorting(base_query, sort)
        paginated_query = paginated_query.offset(pagination.offset).limit(pagination.limit)

        result = await self.session.execute(paginated_query)
        items = result.scalars().all()

        return items, total_count

    async def create(self, instance: ModelType) -> ModelType:
        """Persist a new entity into the database."""
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelType) -> ModelType:
        """Flush changes to an existing entity."""
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        """Hard delete an entity from the database."""
        await self.session.delete(instance)
        await self.session.flush()

    async def soft_delete(self, instance: ModelType) -> ModelType:
        """Logically mark an entity as deleted if it implements SoftDeleteMixin."""
        if isinstance(instance, SoftDeleteMixin):
            from datetime import datetime

            instance.is_deleted = True
            instance.deleted_at = datetime.now(UTC)
            await self.session.flush()
            await self.session.refresh(instance)
        else:
            await self.delete(instance)
        return instance


class TenantRepository(Generic[TenantModelType]):
    """Tenant-isolated repository.

    CRITICAL: Tenant context (organization_id) is mandatory for all operations
    to guarantee zero cross-tenant data leakage.
    """

    def __init__(self, model: type[TenantModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    def _apply_soft_delete_filter(self, query: Any, include_deleted: bool = False) -> Any:
        """Filter out soft-deleted records unless explicitly requested."""
        if not include_deleted and issubclass(self.model, SoftDeleteMixin):
            query = query.where(self.model.is_deleted == False)  # noqa: E712
        return query

    def _apply_sorting(self, query: Any, sort: SortParams | None = None) -> Any:
        """Apply parameterized sorting."""
        if sort is None:
            if hasattr(self.model, "created_at"):
                return query.order_by(self.model.created_at.desc())
            return query.order_by(self.model.id.desc())

        sort_attr = getattr(self.model, sort.sort_by, None)
        sort_column = (
            sort_attr if sort_attr is not None else getattr(self.model, "created_at", self.model.id)
        )

        if sort.order.lower() == "asc":
            return query.order_by(sort_column.asc())
        return query.order_by(sort_column.desc())

    async def get_by_id(
        self,
        organization_id: UUID,
        id: UUID,
        include_deleted: bool = False,
    ) -> TenantModelType | None:
        """Retrieve a tenant-owned entity ensuring organization_id matches."""
        query = select(self.model).where(
            self.model.organization_id == organization_id,
            self.model.id == id,
        )
        query = self._apply_soft_delete_filter(query, include_deleted)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        sort: SortParams | None = None,
        include_deleted: bool = False,
    ) -> tuple[Sequence[TenantModelType], int]:
        """List tenant-owned entities strictly filtered by organization_id."""
        base_query = select(self.model).where(self.model.organization_id == organization_id)
        base_query = self._apply_soft_delete_filter(base_query, include_deleted)

        count_query = select(func.count()).select_from(base_query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()

        paginated_query = self._apply_sorting(base_query, sort)
        paginated_query = paginated_query.offset(pagination.offset).limit(pagination.limit)

        result = await self.session.execute(paginated_query)
        items = result.scalars().all()

        return items, total_count

    async def create(self, organization_id: UUID, instance: TenantModelType) -> TenantModelType:
        """Persist a new tenant-owned entity, forcing its organization_id."""
        instance.organization_id = organization_id
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(
        self,
        organization_id: UUID,
        instance: TenantModelType,
    ) -> TenantModelType:
        """Update a tenant-owned entity after verifying organization boundary."""
        if instance.organization_id != organization_id:
            raise ValueError(
                "Cross-tenant mutation detected: entity does not belong to this organization"
            )
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, organization_id: UUID, instance: TenantModelType) -> None:
        """Hard delete a tenant-owned entity."""
        if instance.organization_id != organization_id:
            raise ValueError(
                "Cross-tenant deletion detected: entity does not belong to this organization"
            )
        await self.session.delete(instance)
        await self.session.flush()

    async def soft_delete(
        self, organization_id: UUID, instance: TenantModelType
    ) -> TenantModelType:
        """Soft delete a tenant-owned entity."""
        if instance.organization_id != organization_id:
            raise ValueError(
                "Cross-tenant soft-deletion detected: entity does not belong to this organization"
            )
        if isinstance(instance, SoftDeleteMixin):
            from datetime import datetime

            instance.is_deleted = True
            instance.deleted_at = datetime.now(UTC)
            await self.session.flush()
            await self.session.refresh(instance)
        else:
            await self.delete(organization_id, instance)
        return instance

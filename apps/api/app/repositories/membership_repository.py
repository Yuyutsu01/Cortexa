"""Membership Repository Module."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import UserRole
from app.models.membership import Membership
from app.repositories.base import BaseRepository
from app.schemas.common import PaginationParams, SortParams


class MembershipRepository(BaseRepository[Membership]):
    """Data access repository for Membership entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Membership, session)

    async def get_membership(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> Membership | None:
        """Find a specific user's membership within an organization."""
        query = (
            select(Membership)
            .options(selectinload(Membership.user))
            .where(
                Membership.organization_id == organization_id,
                Membership.user_id == user_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_by_organization(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        sort: SortParams | None = None,
    ) -> tuple[Sequence[Membership], int]:
        """List all members belonging to an organization with user details attached."""
        base_query = (
            select(Membership)
            .options(selectinload(Membership.user))
            .where(Membership.organization_id == organization_id)
        )

        count_query = select(func.count()).select_from(base_query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()

        paginated_query = self._apply_sorting(base_query, sort)
        paginated_query = paginated_query.offset(pagination.offset).limit(pagination.limit)

        result = await self.session.execute(paginated_query)
        return result.scalars().all(), total_count

    async def count_owners(self, organization_id: UUID) -> int:
        """Count how many active OWNER roles exist in an organization."""
        query = select(func.count(Membership.id)).where(
            Membership.organization_id == organization_id,
            Membership.role == UserRole.OWNER,
            Membership.is_active == True,  # noqa: E712
        )
        result = await self.session.execute(query)
        return result.scalar_one()

"""Organization Repository Module."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership
from app.models.organization import Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Data access repository for Organization entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Organization, session)

    async def get_by_slug(self, slug: str, include_deleted: bool = False) -> Organization | None:
        """Find an organization by URL-friendly slug."""
        query = select(Organization).where(Organization.slug == slug.lower().strip())
        query = self._apply_soft_delete_filter(query, include_deleted)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def slug_exists(self, slug: str) -> bool:
        """Check if an organization slug is already taken."""
        org = await self.get_by_slug(slug, include_deleted=True)
        return org is not None

    async def list_user_organizations(
        self, user_id: UUID
    ) -> Sequence[tuple[Organization, Membership]]:
        """List all organizations that a user has active membership in, along with membership info."""
        query = (
            select(Organization, Membership)
            .join(Membership, Membership.organization_id == Organization.id)
            .where(
                Membership.user_id == user_id,
                Membership.is_active == True,  # noqa: E712
                Organization.is_deleted == False,  # noqa: E712
            )
            .order_by(Organization.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.all()  # type: ignore[return-value]

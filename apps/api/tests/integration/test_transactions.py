"""Integration Tests for Transaction Lifecycle and Rollback Behavior."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization import OrgCreate
from app.services.organization_service import OrganizationService


@pytest.mark.asyncio
async def test_organization_creation_atomic_rollback_on_failure(
    db_session: AsyncSession,
    test_user: User,
) -> None:
    """Verify that if a subsequent step in create_organization fails, the entire transaction rolls back."""
    org_service = OrganizationService(db_session)
    org_repo = OrganizationRepository(db_session)

    # Monkeypatch membership creation to simulate unexpected failure
    async def broken_membership_create(*args, **kwargs):
        raise RuntimeError("Database constraint or network crash during membership creation")

    org_service.membership_repo.create = broken_membership_create  # type: ignore[assignment]

    with pytest.raises(RuntimeError):
        await org_service.create_organization(
            creator_user_id=test_user.id,
            request=OrgCreate(name="Failing Org", slug="failing-org"),
        )

    # Verify that the organization was rolled back and NOT persisted in the database
    persisted_org = await org_repo.get_by_slug("failing-org")
    assert persisted_org is None

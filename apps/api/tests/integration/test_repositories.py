"""Integration Tests for Database Repositories."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import OrgStatus, UserRole
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.repositories.audit_repository import AuditLogRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginationParams


@pytest.mark.asyncio
async def test_user_repository_crud(db_session: AsyncSession) -> None:
    """Verify UserRepository creation, retrieval, and email uniqueness lookup."""
    user_repo = UserRepository(db_session)

    new_user = User(
        email="test_repo@cortexa.ai",
        hashed_password="hashed_pw_here",
        full_name="Repo Tester",
    )
    user = await user_repo.create(new_user)
    assert user.id is not None
    assert user.email == "test_repo@cortexa.ai"

    # Test retrieval by email
    found = await user_repo.get_by_email("TEST_REPO@CORTEXA.AI")
    assert found is not None
    assert found.id == user.id

    # Test soft delete
    await user_repo.soft_delete(user)
    found_after_delete = await user_repo.get_by_email("test_repo@cortexa.ai")
    assert found_after_delete is None

    found_including_deleted = await user_repo.get_by_email(
        "test_repo@cortexa.ai", include_deleted=True
    )
    assert found_including_deleted is not None
    assert found_including_deleted.is_deleted is True


@pytest.mark.asyncio
async def test_organization_and_membership_repository(
    db_session: AsyncSession, test_user: User
) -> None:
    """Verify Organization and Membership repository methods."""
    org_repo = OrganizationRepository(db_session)
    membership_repo = MembershipRepository(db_session)

    org = Organization(
        name="Cortexa HQ",
        slug="cortexa-hq",
        status=OrgStatus.ACTIVE,
    )
    saved_org = await org_repo.create(org)

    membership = Membership(
        organization_id=saved_org.id,
        user_id=test_user.id,
        role=UserRole.OWNER,
    )
    await membership_repo.create(membership)

    # Verify membership retrieval
    found_membership = await membership_repo.get_membership(saved_org.id, test_user.id)
    assert found_membership is not None
    assert found_membership.role == UserRole.OWNER

    # Verify user organization listing
    user_orgs = await org_repo.list_user_organizations(test_user.id)
    assert len(user_orgs) >= 1
    assert any(o.id == saved_org.id for o, _ in user_orgs)

    # Verify owner count
    owner_count = await membership_repo.count_owners(saved_org.id)
    assert owner_count == 1


@pytest.mark.asyncio
async def test_audit_log_repository(db_session: AsyncSession, test_user: User) -> None:
    """Verify AuditLogRepository logging and retrieval."""
    audit_repo = AuditLogRepository(db_session)
    org_id = uuid4()

    log_entry = await audit_repo.log_event(
        action="test.action",
        resource_type="test_resource",
        resource_id="123",
        organization_id=org_id,
        user_id=test_user.id,
        changes={"key": "val"},
        ip_address="127.0.0.1",
    )
    assert log_entry.id is not None

    logs, total = await audit_repo.list_by_organization(
        organization_id=org_id,
        pagination=PaginationParams(page=1, page_size=10),
    )
    assert total == 1
    assert len(logs) == 1
    assert logs[0].action == "test.action"

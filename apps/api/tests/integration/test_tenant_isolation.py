"""Integration Tests for Tenant-Aware Data Access and Isolation."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import OrgStatus
from app.models.organization import Organization
from app.repositories.audit_repository import AuditLogRepository
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.common import PaginationParams


@pytest.mark.asyncio
async def test_tenant_repository_strict_isolation(db_session: AsyncSession) -> None:
    """Verify that TenantRepository strictly isolates data between different organizations."""
    org_repo = OrganizationRepository(db_session)
    audit_repo = AuditLogRepository(db_session)

    # 1. Create Organization A and Organization B
    org_a = await org_repo.create(
        Organization(name="Org Alpha", slug="org-alpha", status=OrgStatus.ACTIVE)
    )
    org_b = await org_repo.create(
        Organization(name="Org Beta", slug="org-beta", status=OrgStatus.ACTIVE)
    )

    # 2. Add audit logs to both organizations
    await audit_repo.log_event(
        action="alpha.event",
        resource_type="document",
        resource_id="doc-1",
        organization_id=org_a.id,
    )
    await audit_repo.log_event(
        action="beta.event",
        resource_type="document",
        resource_id="doc-2",
        organization_id=org_b.id,
    )

    # 3. Query Organization A -> Must only see Alpha records
    logs_a, total_a = await audit_repo.list_by_organization(
        organization_id=org_a.id,
        pagination=PaginationParams(page=1, page_size=10),
    )
    assert total_a == 1
    assert len(logs_a) == 1
    assert logs_a[0].action == "alpha.event"
    assert logs_a[0].organization_id == org_a.id

    # 4. Query Organization B -> Must only see Beta records
    logs_b, total_b = await audit_repo.list_by_organization(
        organization_id=org_b.id,
        pagination=PaginationParams(page=1, page_size=10),
    )
    assert total_b == 1
    assert len(logs_b) == 1
    assert logs_b[0].action == "beta.event"
    assert logs_b[0].organization_id == org_b.id

    # 5. Query nonexistent Organization -> Must return 0
    logs_empty, total_empty = await audit_repo.list_by_organization(
        organization_id=uuid4(),
        pagination=PaginationParams(page=1, page_size=10),
    )
    assert total_empty == 0
    assert len(logs_empty) == 0

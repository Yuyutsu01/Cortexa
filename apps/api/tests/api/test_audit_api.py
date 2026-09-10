"""API Tests for Audit Trail Endpoints."""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_audit_logs_query_flow(
    client: AsyncClient,
    auth_headers: dict[str, str],
    auth_headers_two: dict[str, str],
    test_user_two: User,
) -> None:
    """Verify that domain operations generate audit logs and can be queried with RBAC."""
    # 1. Create organization -> generates ORG_CREATED audit log
    org_res = await client.post(
        "/api/v1/organizations",
        json={"name": "Audit Workspace", "slug": "audit-workspace"},
        headers=auth_headers,
    )
    org_id = org_res.json()["data"]["id"]

    # 2. Add Member -> generates MEMBER_ADDED audit log
    await client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"email": test_user_two.email, "role": "viewer"},
        headers=auth_headers,
    )

    # 3. Owner queries audit trail -> must see both events
    audit_res = await client.get(
        f"/api/v1/organizations/{org_id}/audit-logs",
        headers=auth_headers,
    )
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert len(audit_data["data"]) >= 2
    assert audit_data["pagination"]["total_items"] >= 2
    actions = [log["action"] for log in audit_data["data"]]
    assert "organization.created" in actions
    assert "membership.added" in actions

    # 4. Viewer (User 2) queries audit trail -> must be denied (requires ADMIN or OWNER)
    viewer_audit_res = await client.get(
        f"/api/v1/organizations/{org_id}/audit-logs",
        headers=auth_headers_two,
    )
    assert viewer_audit_res.status_code == 403
    assert viewer_audit_res.json()["error"]["code"] == "PERMISSION_DENIED"

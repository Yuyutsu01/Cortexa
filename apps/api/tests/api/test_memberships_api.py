"""API Tests for Organization Membership and RBAC Endpoints."""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_membership_lifecycle_and_rbac(
    client: AsyncClient,
    auth_headers: dict[str, str],
    auth_headers_two: dict[str, str],
    test_user_two: User,
) -> None:
    """Verify inviting members, updating roles, and RBAC restrictions."""
    # 1. User 1 creates organization
    org_res = await client.post(
        "/api/v1/organizations",
        json={"name": "Team Space", "slug": "team-space"},
        headers=auth_headers,
    )
    org_id = org_res.json()["data"]["id"]

    # 2. Add User 2 as MEMBER
    add_member_payload = {
        "email": test_user_two.email,
        "role": "member",
    }
    add_res = await client.post(
        f"/api/v1/organizations/{org_id}/members",
        json=add_member_payload,
        headers=auth_headers,
    )
    assert add_res.status_code == 201
    assert add_res.json()["data"]["role"] == "member"

    # 3. User 2 can now access the organization
    org_access_res = await client.get(f"/api/v1/organizations/{org_id}", headers=auth_headers_two)
    assert org_access_res.status_code == 200

    # 4. User 2 (MEMBER) cannot add new members (requires ADMIN or OWNER)
    unauthorized_add = await client.post(
        f"/api/v1/organizations/{org_id}/members",
        json={"email": "other@cortexa.ai", "role": "viewer"},
        headers=auth_headers_two,
    )
    assert unauthorized_add.status_code == 403

    # 5. User 1 promotes User 2 to ADMIN
    promote_res = await client.patch(
        f"/api/v1/organizations/{org_id}/members/{test_user_two.id}/role",
        json={"role": "admin"},
        headers=auth_headers,
    )
    assert promote_res.status_code == 200
    assert promote_res.json()["data"]["role"] == "admin"

    # 6. List members with pagination
    list_res = await client.get(f"/api/v1/organizations/{org_id}/members", headers=auth_headers)
    assert list_res.status_code == 200
    members_data = list_res.json()
    assert len(members_data["data"]) == 2
    assert members_data["pagination"]["total_items"] == 2

    # 7. Attempting to delete the last admin is permitted
    self_delete_res = await client.delete(
        f"/api/v1/organizations/{org_id}/members/{test_user_two.id}",  # Delete admin is OK
        headers=auth_headers,
    )
    assert self_delete_res.status_code == 204

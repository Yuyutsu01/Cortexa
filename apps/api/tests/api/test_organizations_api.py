"""API Tests for Organization Workspace Endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_organization_flow(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """Verify organization creation, listing, and detail retrieval."""
    # 1. Create Organization
    create_payload = {
        "name": "Acme Innovations",
        "slug": "acme-innovations",
    }
    create_res = await client.post(
        "/api/v1/organizations", json=create_payload, headers=auth_headers
    )
    assert create_res.status_code == 201
    created_org = create_res.json()["data"]
    assert created_org["name"] == "Acme Innovations"
    assert created_org["slug"] == "acme-innovations"
    org_id = created_org["id"]

    # 2. List user organizations
    list_res = await client.get("/api/v1/organizations", headers=auth_headers)
    assert list_res.status_code == 200
    orgs = list_res.json()["data"]
    assert len(orgs) >= 1
    matching = next(o for o in orgs if o["id"] == org_id)
    assert matching["current_user_role"] == "owner"

    # 3. Get Organization details
    detail_res = await client.get(f"/api/v1/organizations/{org_id}", headers=auth_headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["data"]["name"] == "Acme Innovations"

    # 4. Update Organization name
    update_res = await client.patch(
        f"/api/v1/organizations/{org_id}",
        json={"name": "Acme Global"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["data"]["name"] == "Acme Global"


@pytest.mark.asyncio
async def test_organization_unauthorized_access(
    client: AsyncClient,
    auth_headers: dict[str, str],
    auth_headers_two: dict[str, str],
) -> None:
    """Verify that a user who is not a member cannot access the organization."""
    # User 1 creates org
    create_res = await client.post(
        "/api/v1/organizations",
        json={"name": "Private Org", "slug": "private-org"},
        headers=auth_headers,
    )
    org_id = create_res.json()["data"]["id"]

    # User 2 attempts to access User 1's org
    unauthorized_res = await client.get(f"/api/v1/organizations/{org_id}", headers=auth_headers_two)
    assert unauthorized_res.status_code == 403
    assert unauthorized_res.json()["error"]["code"] == "PERMISSION_DENIED"

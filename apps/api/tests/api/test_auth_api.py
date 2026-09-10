"""API Tests for Authentication Endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient) -> None:
    """Verify complete user registration and login flow."""
    # 1. Register new user
    reg_payload = {
        "email": "newuser@cortexa.ai",
        "password": "Password123!",
        "full_name": "New User",
    }
    reg_response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert reg_data["data"]["email"] == "newuser@cortexa.ai"
    assert "hashed_password" not in reg_data["data"]

    # 2. Login with credentials
    login_payload = {
        "email": "newuser@cortexa.ai",
        "password": "Password123!",
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 3. Access protected /me endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_response = await client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["data"]["email"] == "newuser@cortexa.ai"


@pytest.mark.asyncio
async def test_duplicate_registration_fails(client: AsyncClient) -> None:
    """Verify that registering with an existing email returns 409 Conflict."""
    payload = {
        "email": "duplicate@cortexa.ai",
        "password": "Password123!",
        "full_name": "Duplicate User",
    }
    res1 = await client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409
    error_data = res2.json()
    assert error_data["error"]["code"] == "USER_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_invalid_login_credentials(client: AsyncClient) -> None:
    """Verify that wrong password returns 401 Unauthorized."""
    payload = {
        "email": "registered@cortexa.ai",
        "password": "Password123!",
    }
    await client.post("/api/v1/auth/register", json=payload)

    wrong_login = {
        "email": "registered@cortexa.ai",
        "password": "WrongPassword!",
    }
    res = await client.post("/api/v1/auth/login", json=wrong_login)
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_unauthenticated_protected_endpoint(client: AsyncClient) -> None:
    """Verify that calling /auth/me without authorization returns 401 Unauthorized."""
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "AUTHENTICATION_FAILED"


@pytest.mark.asyncio
async def test_logout_and_token_invalidation(client: AsyncClient) -> None:
    """Verify that logging out invalidates the JWT token and prevents subsequent access."""
    # 1. Register & Login
    payload = {
        "email": "logout_tester@cortexa.ai",
        "password": "Password123!",
        "full_name": "Logout Tester",
    }
    await client.post("/api/v1/auth/register", json=payload)

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "logout_tester@cortexa.ai", "password": "Password123!"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Verify token is active
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200

    # 3. Call logout
    logout_res = await client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert logout_res.json()["message"] == "Successfully logged out"

    # 4. Attempt calling /me again with the now-invalidated token -> Must return 401
    post_logout_me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert post_logout_me_res.status_code == 401
    assert post_logout_me_res.json()["error"]["code"] == "AUTHENTICATION_FAILED"

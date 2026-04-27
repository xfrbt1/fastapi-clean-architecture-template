"""Integration: register → login → CRUD with JWT."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_me_and_user_crud(http_client: AsyncClient) -> None:
    """Full flow against real DB + Redis."""
    reg = await http_client.post(
        "/api/v1/auth/register",
        json={
            "email": "flow@example.com",
            "password": "secretpass123",
            "full_name": "Flow User",
        },
    )
    assert reg.status_code == 201, reg.text
    user_id = reg.json()["id"]

    login = await http_client.post(
        "/api/v1/auth/login",
        json={"email": "flow@example.com", "password": "secretpass123"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = await http_client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "flow@example.com"

    one = await http_client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert one.status_code == 200
    assert one.json()["full_name"] == "Flow User"

    second_hit = await http_client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert second_hit.status_code == 200

    patch = await http_client.patch(
        f"/api/v1/users/{user_id}",
        headers=headers,
        json={"full_name": "Updated Name"},
    )
    assert patch.status_code == 200
    assert patch.json()["full_name"] == "Updated Name"

    listed = await http_client.get("/api/v1/users?limit=10", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) >= 1

    deleted = await http_client.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert deleted.status_code == 204

    missing = await http_client.get(f"/api/v1/users/{user_id}", headers=headers)
    assert missing.status_code == 404

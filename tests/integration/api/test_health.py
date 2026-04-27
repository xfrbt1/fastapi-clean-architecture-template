"""Integration: health endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_payload(http_client: AsyncClient) -> None:
    """GET /api/v1/health returns JSON status fields."""
    response = await http_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data

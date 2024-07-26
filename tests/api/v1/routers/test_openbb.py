"""Test humblapi REST API - `/openbb` router."""

import pytest
from httpx import AsyncClient

from humblapi.core.config import Config
from humblapi.main import app

config = Config()


@pytest.mark.asyncio()
async def test_latest_price():
    """Test that the latest price endpoint returns successfully."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"{config.API_V1_STR}/latest-price")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, dict) for item in data)
    assert all("symbol" in item and "last_price" in item for item in data)


@pytest.mark.asyncio()
async def test_last_close():
    """Test that the last close endpoint returns successfully."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"{config.API_V1_STR}/last-close")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, dict) for item in data)
    assert all("symbol" in item and "prev_close" in item for item in data)


@pytest.mark.asyncio()
async def test_custom_symbols():
    """Test that custom symbols can be provided to the endpoints."""
    custom_symbols = "GOOGL,AMZN,META"
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"{config.API_V1_STR}/latest-price?symbols={custom_symbols}"
        )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert set(item["symbol"] for item in data) == set(
        custom_symbols.split(",")
    )


@pytest.mark.asyncio()
async def test_invalid_provider():
    """Test that an invalid provider returns an error."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"{config.API_V1_STR}/latest-price?provider=invalid_provider"
        )
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio()
async def test_empty_symbols():
    """Test that empty symbols return an error."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"{config.API_V1_STR}/latest-price?symbols=")
    assert response.status_code == 400  # Unprocessable Entity

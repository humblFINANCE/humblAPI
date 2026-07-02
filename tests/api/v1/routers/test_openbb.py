"""Test humblapi REST API - `/openbb` router."""

import http

from fastapi.testclient import TestClient

from humblapi.core.config import Config

config = Config()

EXPECTED_CUSTOM_SYMBOL_COUNT = 3


def test_latest_price(client: TestClient):
    """Test that the latest price endpoint returns successfully."""
    response = client.get(f"{config.API_V1_STR}/latest-price")
    assert response.status_code == http.HTTPStatus.OK
    data = response.json()["response_data"]
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, dict) for item in data)
    assert all("symbol" in item and "last_price" in item for item in data)


def test_last_close(client: TestClient):
    """Test that the last close endpoint returns successfully."""
    response = client.get(f"{config.API_V1_STR}/last-close")
    assert response.status_code == http.HTTPStatus.OK
    data = response.json()["response_data"]["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(item, dict) for item in data)
    assert all("symbol" in item and "prev_close" in item for item in data)


def test_custom_symbols(client: TestClient):
    """Test that custom symbols can be provided to the endpoints."""
    custom_symbols = "GOOGL,AMZN,META"
    response = client.get(
        f"{config.API_V1_STR}/latest-price?symbols={custom_symbols}"
    )
    assert response.status_code == http.HTTPStatus.OK
    data = response.json()["response_data"]
    assert len(data) == EXPECTED_CUSTOM_SYMBOL_COUNT
    assert {item["symbol"] for item in data} == set(custom_symbols.split(","))


def test_invalid_provider(client: TestClient):
    """Test that an invalid provider returns an error."""
    response = client.get(
        f"{config.API_V1_STR}/latest-price?provider=invalid_provider"
    )
    assert response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY


def test_empty_symbols(client: TestClient):
    """Test that empty symbols return an error."""
    response = client.get(f"{config.API_V1_STR}/latest-price?symbols=")
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

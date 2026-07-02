"""Test humblapi REST API."""

import http

import httpx
from fastapi.testclient import TestClient

from humblapi.core.config import Config

config = Config()


def test_read_root(client: TestClient) -> None:
    """Test that reading the root is successful."""
    response = client.get(f"{config.API_V1_STR}/")
    assert httpx.codes.is_success(response.status_code)


def test_health_endpoint(client: TestClient):
    """Test that the health endpoint returns a successful response."""
    response = client.get(f"{config.API_V1_STR}/health")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "response_data": None,
        "message": "humblAPI is HEALTHY",
        "warnings": None,
        "extra": None,
        "status_code": 200,
    }

"""Test humblapi REST API."""

import httpx
from fastapi.testclient import TestClient

from humblapi.main import app

client = TestClient(app)


def test_read_root() -> None:
    """Test that reading the root is successful."""
    response = client.get("/")
    assert httpx.codes.is_success(response.status_code)


def test_health_endpoint():
    """Test that the health endpoint returns a successful response."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"message": "API is healthy"},
        "status_code": 200,
    }

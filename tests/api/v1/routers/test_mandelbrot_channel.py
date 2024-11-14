"""Test humblapi REST API - `/humblCHANNEL` router."""

import httpx
from fastapi.testclient import TestClient
from humblapi.core.config import Config

from humblapi.main import app

client = TestClient(app)
config = Config()


def test_humbl_channel_root() -> None:
    """Test that reading the root is successful."""
    response = client.get(f"{config.API_V1_STR}/humblCHANNEL")
    assert httpx.codes.is_success(response.status_code)

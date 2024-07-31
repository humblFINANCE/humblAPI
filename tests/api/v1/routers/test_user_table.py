"""Test humblapi REST API - `/user_table` router"""

import httpx
from fastapi.testclient import TestClient

from humblapi.core.config import Config
from humblapi.main import app

client = TestClient(app)
config = Config()


def test_user_table_root() -> None:
    """Test that reading the root is successful."""
    response = client.get(f"{config.API_V1_STR}/user-table")
    assert httpx.codes.is_success(response.status_code)

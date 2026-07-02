"""Test humblapi REST API - `/portfolio` router"""

import httpx
from fastapi.testclient import TestClient

from humblapi.core.config import Config

config = Config()


def test_portfolio_root(client: TestClient) -> None:
    """Test that reading the root is successful."""
    response = client.get(f"{config.API_V1_STR}/watchlist_table")
    assert httpx.codes.is_success(response.status_code)

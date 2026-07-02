"""Shared pytest fixtures for humblAPI tests."""

import pytest
from fastapi.testclient import TestClient

from humblapi.main import app


@pytest.fixture(scope="session")
def client():
    """Provide a session-wide `TestClient` with FastAPI's lifespan run.

    Using `TestClient` as a context manager triggers the app's lifespan
    events (e.g. `FastAPICache.init(...)` in `main.py`) - without it, any
    route decorated with `@cache(...)` fails with
    `AssertionError: You must call init first!`.

    Session-scoped and shared: `TestClient` runs requests through an
    internal anyio portal (its own event loop). The lifespan's Redis
    connections (FastAPICache/FastAPILimiter) are bound to *that specific*
    portal's loop - creating a second, separate `TestClient(app)` instance
    for actual requests would open a different portal/loop, and any route
    that awaits those Redis connections would fail with
    "Future attached to a different loop" (or hang). All tests must reuse
    this exact instance, not construct their own `TestClient(app)`.
    """
    with TestClient(app) as test_client:
        yield test_client

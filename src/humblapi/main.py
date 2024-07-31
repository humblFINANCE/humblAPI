"""humblapi REST API."""

import logging
from contextlib import asynccontextmanager

import coloredlogs
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware

from humblapi.api.v1.routers import openbb, portfolio, toolbox
from humblapi.core.config import config
from humblapi.core.env import Env
from humblapi.core.middleware import TimeLogMiddleware
from humblapi.core.utils import raise_http_exception

env = Env()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application's lifecycle.

    The code before 'yield' runs at startup, after 'yield' at shutdown.
    """
    if config.DEVELOPMENT:
        redis = await aioredis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=1,
            decode_responses=False,
        )
    else:
        redis = await aioredis.Redis().from_url(config.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers:
        logging.root.removeHandler(handler)
    # Add coloredlogs' coloured StreamHandler to the root logger.
    coloredlogs.install()
    yield
    # Clean up and release the resources


# Setup App
app = FastAPI(
    title=config.PROJECT_NAME,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)

# Add Middleware
middleware = TimeLogMiddleware(some_attribute="some_attribute_here_if_needed")
app.add_middleware(BaseHTTPMiddleware, dispatch=middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add Routers
app.include_router(portfolio.router)
app.include_router(toolbox.router)
app.include_router(openbb.router)


@app.get("/")
@cache(expire=60)
async def read_root() -> dict:
    """Read root."""
    return {"message": "Welcome to the humblapi API"}


@app.get("/health")
@cache(expire=60)
async def health_check():
    """
    Health check endpoint.

    Returns
    -------
        dict: A JSON response indicating the API's health status and HTTP status code.
    """
    return {"data": {"message": "API is healthy"}, "status_code": 200}


@app.get("/redis-health")
@cache(expire=10)
async def redis_health_check():
    """
    Check the health of the Redis connection.

    Returns
    -------
        dict: A JSON response indicating the Redis connection status and HTTP status code.
    """
    try:
        redis_backend = FastAPICache.get_backend()
        if isinstance(redis_backend, RedisBackend):
            redis = redis_backend.redis
            if await redis.ping():
                return {"data": {"message": "PONG"}, "status_code": 200}
        raise_http_exception(500, "Redis connection failed")
    except Exception as e:
        raise_http_exception(500, f"Redis connection error: {e!s}")


@app.get("/flush-redis")
async def flush_redis(
    token: str = Query(description="Secret API token for flushing Redis"),
):
    """
    Flush the Redis database.

    Parameters
    ----------
    token : str
        Secret API token for authentication.

    Returns
    -------
    dict
        A dictionary containing a success message and status code.

    Raises
    ------
    HTTPException
        If the token is invalid or if there's an error flushing Redis.
    """
    if token != config.FLUSH_API_TOKEN:
        raise_http_exception(403, "Invalid API token")

    try:
        redis_backend = FastAPICache.get_backend()
        if isinstance(redis_backend, RedisBackend):
            redis = redis_backend.redis
            await redis.flushdb()
            return {
                "data": {"message": "Redis database flushed successfully"},
                "status_code": 200,
            }
        raise_http_exception(500, "Redis backend not found")
    except Exception as e:
        raise_http_exception(500, f"Error flushing Redis: {e!s}")

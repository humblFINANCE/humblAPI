from fastapi import FastAPI, HTTPException, Query
from fastapi.routing import APIRouter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from humblapi.core.config import config
from humblapi.core.logger import setup_logger
from humblapi.core.standard_models.abstract.responses import HumblResponse
from humblapi.core.utils import raise_http_exception, redis_delete_pattern

router = APIRouter(
    prefix=config.API_V1_STR,
    tags=["core"],
)
logger = setup_logger(name="humblapi.api.v1.routers.core")


@router.get("/", response_model=HumblResponse[None])
@cache(expire=60)
async def read_root() -> HumblResponse[None]:
    """Read root."""
    return HumblResponse(
        response_data=None,
        message="Welcome to the humblapi API",
        status_code=200,
    )


@router.get("/health", response_model=HumblResponse[None])
@cache(expire=60)
async def health_check() -> HumblResponse[None]:
    """
    Health check endpoint.

    Returns
    -------
        HumblResponse[None]
    """
    return HumblResponse(
        response_data=None,
        status_code=200,
        message="humblAPI is HEALTHY",
    )


@router.get("/redis-health", response_model=HumblResponse[dict])
@cache(expire=10)
async def redis_health_check() -> HumblResponse[dict]:
    """
    Check the health of the Redis connection.

    Returns
    -------
        HumblResponse[dict]: A response indicating the Redis connection status, host, and HTTP status code.
    """
    try:
        redis_backend = FastAPICache.get_backend()
        if isinstance(redis_backend, RedisBackend):
            redis = redis_backend.redis
            if await redis.ping():
                connection_kwargs = redis.connection_pool.connection_kwargs
                host = connection_kwargs.get("host", "Unknown")
                port = connection_kwargs.get("port", "Unknown")
                username = connection_kwargs.get("username", "Unknown")
                return HumblResponse(
                    response_data={
                        "host": host,
                        "username": username,
                        "port": port,
                    },
                    message="PONG",
                    status_code=200,
                )
        raise_http_exception(500, "Redis connection failed")
    except Exception as e:
        raise_http_exception(500, f"Redis connection error: {e!s}")


@router.get("/flush-redis", response_model=HumblResponse[dict])
async def flush_redis(
    token: str = Query(description="Secret API token for flushing Redis"),
    fastapi_cache_only: bool = Query(
        description="If true, ONLY flush the FastAPI cache. This removes all keys with the 'fastapi-cache:' prefix.",
        default=False,
    ),
) -> HumblResponse[dict]:
    """
    Flush the Redis database or only the FastAPI cache.

    Parameters
    ----------
    token : str
        Secret API token for authentication.
    fastapi_cache_only : bool
        If true, only flush the FastAPI cache.

    Returns
    -------
    HumblResponse[dict]
        A HumblResponse containing a success message, status code, and records deleted.

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
            if fastapi_cache_only:
                records_deleted = await redis_delete_pattern(
                    redis, "fastapi-cache:*"
                )
                return HumblResponse(
                    response_data={
                        "records_deleted": records_deleted,
                    },
                    message="FastAPI cache was flushed successfully.",
                    status_code=200,
                )
            else:
                records = await redis.dbsize()
                await redis.flushdb()
                return HumblResponse(
                    response_data={
                        "records_deleted": records,
                    },
                    message="Redis database flushed successfully.",
                    status_code=200,
                )
        raise_http_exception(500, "Redis backend not found")
    except Exception as e:
        raise_http_exception(500, f"Error flushing Redis: {e!s}")

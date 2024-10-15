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
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from redis import asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware

from humblapi.api.v1.routers import (
    core,
    humbl_channel,
    humbl_compass,
    openbb,
    portfolio,
)
from humblapi.core.config import config
from humblapi.core.env import Env
from humblapi.core.logger import setup_logger
from humblapi.core.middleware import TimeLogMiddleware

env = Env()
logger = setup_logger("humblAPI Lifespan", level=env.LOGGER_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application's lifecycle.

    The code before 'yield' runs at startup, after 'yield' at shutdown.
    """
    try:
        if config.DEVELOPMENT:
            redis = await aioredis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=1,
                decode_responses=False,
            )
        else:
            redis = await aioredis.Redis().from_url(config.REDIS_URL)

        # Initialize FastAPICache
        try:
            FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
            logger.info("FastAPICache initialized successfully")
        except Exception as e:
            logger.exception(f"Failed to initialize FastAPICache: {e!s}")

        # Initialize FastAPILimiter
        try:
            await FastAPILimiter.init(redis)
            logger.info("FastAPILimiter initialized successfully")
        except Exception as e:
            logger.exception(f"Failed to initialize FastAPILimiter: {e!s}")

        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        # Add coloredlogs' coloured StreamHandler to the root logger.
        coloredlogs.install()

        yield

        # Clean up and release the resources
        try:
            await FastAPILimiter.close()
            logger.info("FastAPILimiter closed successfully")
        except Exception as e:
            logger.exception(f"Failed to close FastAPILimiter: {e!s}")

    except Exception as e:
        logger.exception(f"An error occurred during lifespan setup: {e!s}")


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
    expose_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add Routers
app.include_router(portfolio.router)
app.include_router(humbl_channel.router)
app.include_router(openbb.router)
app.include_router(core.router)
app.include_router(humbl_compass.router)

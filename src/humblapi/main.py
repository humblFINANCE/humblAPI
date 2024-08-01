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

from humblapi.api.v1.routers import openbb, portfolio, toolbox, core
from humblapi.core.config import config
from humblapi.core.env import Env
from humblapi.core.middleware import TimeLogMiddleware

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
app.include_router(core.router)

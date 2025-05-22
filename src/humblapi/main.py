"""humblapi REST API."""

import logging
from contextlib import asynccontextmanager

import coloredlogs
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_limiter import FastAPILimiter
from redis import asyncio as aioredis
from starlette.middleware.base import BaseHTTPMiddleware

from humblapi.api.v1.routers import core, openbb, portfolio, toolbox
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
            msg = f"Failed to initialize FastAPICache: {e!s}"
            logger.exception(msg)

        # Initialize FastAPILimiter
        try:
            await FastAPILimiter.init(redis)
            logger.info("FastAPILimiter initialized successfully")
        except Exception as e:
            msg = f"Failed to initialize FastAPILimiter: {e!s}"
            logger.exception(msg)

        # Remove all handlers associated with the root logger object.
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        # Add coloredlogs' coloured StreamHandler to the root logger.
        coloredlogs.install()

        # TODO: Add OpenBB login with OpenBBAPIClient
        # if config.OBB_PAT:
        #     obb.account.login(pat=config.OBB_PAT, remember_me=True)
        # else:
        #     logger.warning(
        #         "No OBB PAT provided, skipping OpenBB login, alternative providers will be unavailable"
        #     )

        yield

        # Clean up and release the resources
        try:
            await FastAPILimiter.close()
            logger.info("FastAPILimiter closed successfully")
        except Exception as e:
            msg = f"Failed to close FastAPILimiter: {e!s}"
            logger.exception(msg)

    except Exception as e:
        msg = f"An error occurred during lifespan setup: {e!s}"
        logger.exception(msg)


# Setup App
app = FastAPI(
    title=config.PROJECT_NAME,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    version="0.19.0",
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
app.include_router(portfolio.router, prefix=config.API_V1_STR)
app.include_router(toolbox.router, prefix=config.API_V1_STR)
app.include_router(openbb.router, prefix=config.API_V1_STR)
app.include_router(core.router, prefix=config.API_V1_STR)

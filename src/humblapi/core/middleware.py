import logging
import time

from fastapi import Request

logger = logging.getLogger(__name__)


class MyMiddleware:
    def __init__(
        self,
        some_attribute: str,
    ):
        self.some_attribute = some_attribute

    async def __call__(self, request: Request, call_next):
        logger.info("I'm a middleware!")
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()

        logger.info(f"execution time: {end_time - start_time:.6f} seconds")
        return response

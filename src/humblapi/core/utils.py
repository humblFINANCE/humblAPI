from typing import Any
from fastapi.exceptions import HTTPException

import orjson
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from fastapi_cache import Coder
from redis.asyncio.client import Redis


class ORJsonCoder(Coder):
    """
    A custom coder class for encoding and decoding JSON using orjson.

    This class extends the Coder class from fastapi_cache and provides methods
    for encoding Python objects to JSON bytes and decoding JSON bytes back to
    Python objects using the orjson library.

    Methods
    -------
    encode(value: Any) -> bytes | Any
        Encode a Python object to JSON bytes or return ORJSONResponse as is.
    decode(value: bytes) -> Any
        Decode JSON bytes to a Python object.
    """

    @classmethod
    def encode(cls, value: Any) -> bytes | Any:
        """
        Encode a Python object to JSON bytes or return ORJSONResponse as is.

        Parameters
        ----------
        value : Any
            The Python object to be encoded.

        Returns
        -------
        bytes | Any
            The encoded JSON as bytes or the original ORJSONResponse object.
        """
        return orjson.dumps(
            value,
            default=jsonable_encoder,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )

    @classmethod
    def decode(cls, value: bytes) -> Any:
        """
        Decode JSON bytes to a Python object.

        Parameters
        ----------
        value : bytes
            The JSON bytes to be decoded.

        Returns
        -------
        Any
            The decoded Python object.
        """
        return orjson.loads(value)


def request_key_builder(
    func,
    namespace: str = "",
    request: Request | None = None,
    response: Response | None = None,
    *args,
    **kwargs,
):
    return ":".join(
        [
            namespace,
            request.method.lower(),
            request.url.path,
            repr(sorted(request.query_params.items())),
        ]
    )


def raise_http_exception(status_code: int, detail: str):
    """
    Raise an HTTPException with the given status code and detail.

    Parameters
    ----------
    status_code : int
        The HTTP status code for the exception.
    detail : str
        The detail message for the exception.

    Raises
    ------
    HTTPException
        An exception with the specified status code and detail.
    """
    raise HTTPException(status_code=status_code, detail=detail)


async def redis_delete_pattern(redis: Redis, pattern: str):
    """
    Delete Redis keys matching a given pattern.

    Parameters
    ----------
    pattern : str
        The pattern to match Redis keys against.

    Returns
    -------
    None

    Notes
    -----
    This function uses Redis' SCAN command to iterate over keys
    matching the given pattern and deletes them.
    """
    records = await redis.dbsize()
    async for key in redis.scan_iter(match=pattern):
        await redis.delete(key)
    records_left = await redis.dbsize()
    records_deleted = records - records_left
    return records_deleted

from typing import Any

import orjson
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from fastapi_cache import Coder


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

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

# Generic typing is used here to specify the return type for response_data.
# This allows for flexible and type-safe responses where T can be any valid type.
# For example, HumblResponse[dict] would indicate that response_data is a dictionary,
# while HumblResponse[List[str]] would indicate that response_data is a list of strings.
# This approach enhances type checking and provides better IDE support for consumers of the API.


class HumblResponse(BaseModel, Generic[T]):
    response_data: T | None = None
    message: str | None = None
    status_code: int = Field(200, description="HTTP status code")

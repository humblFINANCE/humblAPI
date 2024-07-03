from fastapi import APIRouter, Depends
from humbldata.portfolio.analytics.user_table.helpers import (
    aggregate_user_table_data,
)

from humblapi.core.config import Config

config = Config()
router = APIRouter(
    prefix=config.API_V1_STR,
    tags=["user"],
)


@router.get("/user-table")
async def user_table_route():
    """
    Retrieve user table data for specific symbols.

    This endpoint aggregates user table data for the specified symbols
    (XLU, XLE, and AAPL) using the aggregate_user_table_data function.
    The aggregated data is then collected and converted to a dictionary.

    Returns
    -------
    dict
        A dictionary containing the aggregated user table data for the
        specified symbols. The dict of a humblObject with `as_series=False` is
        identical to a JSON format.

    Notes
    -----
    The function uses the aggregate_user_table_data helper from the
    humbldata.portfolio.analytics.user_table.helpers module to perform
    the data aggregation.
    """
    user_table_data = (
        (await aggregate_user_table_data(symbols=["XLU", "XLE", "AAPL"]))
        .collect()
        .to_dict(as_series=False)
    )

    return user_table_data


# Add more routes as needed

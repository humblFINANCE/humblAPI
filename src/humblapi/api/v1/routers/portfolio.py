"""
Portfolio API router.

This router is used to handle requests for the humblAPI Portfolio <context>
"""

from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query
from fastapi_cache.decorator import cache
from humbldata.core.utils.descriptions import QUERY_DESCRIPTIONS
from humbldata.portfolio.portfolio_controller import Portfolio

from humblapi.core.config import Config

config = Config()
router = APIRouter(
    prefix=config.API_V1_STR,
    tags=["portfolio"],
)


@router.get("/user-table")
@cache(expire=86000, namespace="user_table")
async def user_table_route(
    symbols: Annotated[
        str, Query(description=QUERY_DESCRIPTIONS.get("symbols", ""))
    ] = "AAPL,NVDA,TSLA",
    membership: Annotated[
        Literal["anonymous", "peon", "premium", "power", "permanent", "admin"],
        Query(description=QUERY_DESCRIPTIONS.get("membership", "")),
    ] = "peon",
):
    """
    Retrieve user table data for the specified portfolio symbols.

    This endpoint aggregates user table data for the symbols provided in the query parameter.
    The aggregated data is then collected and converted to a dictionary.

    Parameters
    ----------
    symbols : str, optional
        A comma-separated string of stock symbols (e.g., "AAPL,MSFT,NVDA").
        Default is "AAPL,NVDA,TSLA" if no symbols are provided.

    membership : Literal["anonymous", "peon", "premium", "power", "permanent", "admin"], optional
        The user role or membership level. Default is "peon".

    Returns
    -------
    dict : UserTableData
        A dictionary containing the aggregated user table data for the
        specified symbols. The dict of a HumblObject with `as_series=False` is
        identical to a JSON format.
        UserTableData is a pandera.polars model that is used to validate the
        output from humblDATA.

    Raises
    ------
    HTTPException
        If the symbols parameter is an empty string.

    Notes
    -----
    The function uses the `Portfolio` class from humblDATA to perform
    the data aggregation.
    """
    if symbols == "":
        raise HTTPException(
            status_code=400, detail="Symbols parameter cannot be empty"
        )

    # Split the symbols string into a list
    symbol_list = symbols.split(",")

    portfolio = Portfolio(symbols=symbol_list, membership=membership)

    user_table_data = (await portfolio.analytics.user_table()).to_dict(
        row_wise=True, as_series=False
    )
    return user_table_data


# Add more routes as needed

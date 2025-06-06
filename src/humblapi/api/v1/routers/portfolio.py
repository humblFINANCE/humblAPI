"""
Portfolio API router.

This router is used to handle requests for the humblAPI Portfolio <context>
"""

import datetime as dt
from typing import Annotated, Literal

from fastapi import APIRouter, Query
from fastapi.responses import ORJSONResponse
from fastapi_cache.decorator import cache
from humbldata.core.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from humbldata.portfolio.portfolio_controller import Portfolio
from pydantic import BaseModel, Field, ValidationError

from humblapi.core.logger import setup_logger
from humblapi.core.standard_models.abstract.responses import HumblResponse
from humblapi.core.utils import ORJsonCoder, raise_http_exception

router = APIRouter(tags=["portfolio"])

logger = setup_logger(name="humblapi.api.v1.routers.portfolio")


class WatchlistTableData(BaseModel):
    date: str | dt.datetime = Field(
        ..., description=DATA_DESCRIPTIONS.get("date", "")
    )
    symbol: str = Field(..., description=DATA_DESCRIPTIONS.get("symbol", ""))
    buy_price: float = Field(
        ..., description=DATA_DESCRIPTIONS.get("buy_price", "")
    )
    last_price: float = Field(
        ..., description=DATA_DESCRIPTIONS.get("last_price", "")
    )
    sector: str | None = Field(
        ..., description=DATA_DESCRIPTIONS.get("sector", "")
    )
    sell_price: float = Field(
        ..., description=DATA_DESCRIPTIONS.get("sell_price", "")
    )
    ud_pct: str = Field(..., description=DATA_DESCRIPTIONS.get("ud_pct", ""))
    ud_ratio: float = Field(
        ..., description=DATA_DESCRIPTIONS.get("ud_ratio", "")
    )
    asset_class: str = Field(
        ..., description=DATA_DESCRIPTIONS.get("asset_class", "")
    )
    momentum_signal: float | None = Field(
        ..., description=DATA_DESCRIPTIONS.get("momentum_signal", "")
    )


class WatchlistTableResponse(BaseModel):
    data: list[WatchlistTableData]


@router.get(
    "/watchlist_table",
    response_class=ORJSONResponse,
    response_model=HumblResponse[WatchlistTableResponse],
)
@cache(expire=86000, namespace="portfolio", coder=ORJsonCoder)
async def portfolio_route(
    symbols: Annotated[
        str, Query(description=QUERY_DESCRIPTIONS.get("symbols", ""))
    ] = "AAPL,NVDA,TSLA",
    membership: Annotated[
        Literal[
            "anonymous",
            "humblPEON",
            "humblPREMIUM",
            "humblPOWER",
            "humblPERMANENT",
            "admin",
        ],
        Query(description=QUERY_DESCRIPTIONS.get("membership", "")),
    ] = "humblPEON",
):
    """
    Retrieve portfolio data for the specified portfolio symbols.

    This endpoint aggregates portfolio data for the symbols provided in the query parameter.
    The aggregated data is then collected and converted to a dictionary.

    Parameters
    ----------
    symbols : str, optional
        A comma-separated string of stock symbols (e.g., "AAPL,MSFT,NVDA").
        Default is "AAPL,NVDA,TSLA" if no symbols are provided.

    membership : Literal["anonymous", "humblPEON", "humblPREMIUM", "humblPOWER", "humblPERMANENT", "admin"], optional
        The user role or membership level. Default is "humblPEON".

    Returns
    -------
    dict : PortfolioData
        A dictionary containing the aggregated user table data for the
        specified symbols. The dict of a HumblObject with `as_series=False` is
        identical to a JSON format.
        PortfolioData is a pandera.polars model that is used to validate the
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
    try:
        if symbols == "":
            raise_http_exception(400, "Symbols parameter cannot be empty")

        # Split the symbols string into a list
        symbol_list = symbols.split(",")

        portfolio = Portfolio(symbols=symbol_list, membership=membership)

        watchlist_table_data = (
            await portfolio.analytics.watchlist_table()
        ).to_dict(row_wise=True, as_series=False)

        watchlist_table_response = WatchlistTableResponse(
            data=[WatchlistTableData(**item) for item in watchlist_table_data]
        )
        return HumblResponse[WatchlistTableResponse](
            response_data=watchlist_table_response,
            status_code=200,
        )
    except ValidationError as ve:
        msg = f"Validation error: {ve!s}"
        logger.exception(msg)
        raise_http_exception(422, msg)
    except Exception as e:
        msg = f"Internal server error: {e!s}"
        logger.exception(msg)
        raise_http_exception(500, msg)

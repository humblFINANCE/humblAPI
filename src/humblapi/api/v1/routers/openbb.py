"""
OpenBB API router.

This router is used to handle requests for the humblAPI OpenBB Data<context>
"""

from typing import Annotated

from fastapi import APIRouter, Query
from humbldata.core.utils.constants import (
    OBB_EQUITY_PRICE_QUOTE_PROVIDERS,
)
from humbldata.core.utils.descriptions import QUERY_DESCRIPTIONS
from humbldata.core.utils.openbb_helpers import (
    aget_last_close,
    aget_latest_price,
)

from humblapi.core.config import Config

config = Config()
router = APIRouter(
    prefix=config.API_V1_STR,
    tags=["openbb"],
)


@router.get("/latest-price")
async def latest_price(
    symbols: Annotated[
        str, Query(description=QUERY_DESCRIPTIONS.get("symbols", ""))
    ] = "AAPL,NVDA,TSLA",
    provider: Annotated[
        OBB_EQUITY_PRICE_QUOTE_PROVIDERS,
        Query(description="The data provider for fetching stock prices."),
    ] = "yfinance",
):
    """
    Retrieve latest OpenBB price data for the specified symbols.

    This endpoint fetches the latest stock price data for the symbols provided in the query parameter
    using the specified provider asynchronously.

    Parameters
    ----------
    symbols : str, optional
        A comma-separated string of stock symbols (e.g., "AAPL,MSFT,NVDA").
        Default is "AAPL,NVDA,TSLA" if no symbols are provided.
    provider : OBB_EQUITY_PRICE_QUOTE_PROVIDERS, optional
        The data provider for fetching stock prices. Default is "yfinance".

    Returns
    -------
    dict
        A dictionary containing the latest price data for the specified symbols.
        The dictionary includes 'symbol' and 'last_price' for each queried symbol.

    Notes
    -----
    This function uses the `aget_latest_price` function from humblDATA to fetch the data.
    The function handles both ETFs and Equities, but not futures or options.
    """
    # Convert the comma-separated string to a list of symbols
    symbol_list = symbols.split(",")

    # Fetch the latest price data
    lf = await aget_latest_price(symbol_list, provider)

    # Convert the LazyFrame to a dictionary
    result = lf.collect().to_dicts()

    return result


@router.get("/last-close")
async def last_close(
    symbols: Annotated[
        str, Query(description=QUERY_DESCRIPTIONS.get("symbols", ""))
    ] = "AAPL,NVDA,TSLA",
    provider: Annotated[
        OBB_EQUITY_PRICE_QUOTE_PROVIDERS,
        Query(description="The data provider for fetching stock prices."),
    ] = "yfinance",
):
    """
    Retrieve the last closing price for the specified symbols using OpenBB.

    This endpoint fetches the last closing price data for the symbols provided in the query parameter
    using the specified provider asynchronously.

    Parameters
    ----------
    symbols : str, optional
        A comma-separated string of stock symbols (e.g., "AAPL,MSFT,NVDA").
        Default is "AAPL,NVDA,TSLA" if no symbols are provided.
    provider : OBB_EQUITY_PRICE_QUOTE_PROVIDERS, optional
        The data provider for fetching stock prices. Default is "yfinance".

    Returns
    -------
    dict
        A dictionary containing the last closing price data for the specified symbols.
        The dictionary includes 'symbol' and 'prev_close' for each queried symbol.

    Notes
    -----
    This function uses the `aget_last_close` function to fetch the data.
    The function handles both ETFs and Equities, but not futures or options.
    """
    # Convert the comma-separated string to a list of symbols
    symbol_list = symbols.split(",")

    # Fetch the last closing price data
    lf = await aget_last_close(symbol_list, provider)

    # Convert the LazyFrame to a dictionary
    result = lf.collect().to_dicts()

    return result
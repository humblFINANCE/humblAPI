from fastapi import APIRouter, Depends
from humbldata.core.standard_models.portfolio.analytics.user_table import (
    UserTableData,
    UserTableQueryParams,
)
from humbldata.portfolio.portfolio_controller import Portfolio

from humblapi.core.config import Config

config = Config()
router = APIRouter(
    prefix=config.API_V1_STR,
    tags=["user"],
)


@router.get("/user-table")
async def user_table_route(
    symbols: str = "AAPL,NVDA,TSLA", membership: str = "peon"
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
    membership : str, optional
        The user role or membership level. Default is "peon".

    Returns
    -------
    dict : UserTableData
        A dictionary containing the aggregated user table data for the
        specified symbols. The dict of a HumblObject with `as_series=False` is
        identical to a JSON format.
        UserTableData is a pandera.polars model that is used to validate the
        output from humblDATA.

    Notes
    -----
    The function uses the `Portfolio` class from humblDATA to perform
    the data aggregation.
    """
    # Split the symbols string into a list
    symbol_list = symbols.split(",")

    portfolio = Portfolio(symbols=symbol_list, user_role=membership)

    user_table_data = (await portfolio.analytics.user_table()).to_dict(
        row_wise=True, as_series=False
    )
    return user_table_data


# Add more routes as needed

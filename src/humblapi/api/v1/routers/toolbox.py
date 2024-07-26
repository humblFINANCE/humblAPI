"""
Toolbox API router.

This router is used to handle requests for the humblAPI Toolbox <context>
"""

import datetime as dt
from typing import Literal

import orjson
import pytz
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import ORJSONResponse
from fastapi_cache.decorator import cache
from humbldata.toolbox.toolbox_controller import Toolbox

from humblapi.core.config import Config
from humblapi.core.logger import setup_logger
from humblapi.core.utils import ORJsonCoder

config = Config()
router = APIRouter(
    prefix=config.API_V1_STR,
    tags=["toolbox"],
)
logger = setup_logger(name="humblapi.api.v1.routers.toolbox")


def validate_symbols(symbols):
    if not symbols:
        msg = "No symbols provided"
        raise ValueError(msg)
    return symbols


@router.get("/mandelbrot-channel", response_class=ORJSONResponse)
@cache(expire=86000, namespace="mandelbrot_channel", coder=ORJsonCoder)
async def mandelbrot_channel_route(
    symbols: str = Query(
        "AAPL,NVDA,TSLA",
        description="A comma-separated string of stock symbols",
    ),
    interval: str = Query("1d", description="The interval for data points"),
    start_date: str = Query(
        "2000-01-01", description="The start date for the data range"
    ),
    end_date: str = Query(
        default_factory=lambda: dt.datetime.now(
            tz=pytz.timezone("America/New_York")
        ).date(),
        description="The end date for the data range",
    ),
    provider: str = Query("yfinance", description="The data provider to use"),
    window: str = Query("1mo", description="The window size for calculations"),
    rv_adjustment: bool = Query(
        True,
        description="Whether to adjust the calculation for realized volatility",
    ),
    rv_method: Literal[
        "std",
        "parkinson",
        "garman_klass",
        "gk",
        "hodges_tompkins",
        "ht",
        "rogers_satchell",
        "rs",
        "yang_zhang",
        "yz",
        "squared_returns",
        "sq",
    ] = Query(
        "std", description="The method to calculate the realized volatility"
    ),
    rs_method: Literal["RS", "RS_min", "RS_max", "RS_mean"] = Query(
        "RS", description="The method to use for Range/STD calculation"
    ),
    rv_grouped_mean: bool = Query(
        False,
        description="Whether to calculate the mean value of realized volatility over multiple window lengths",
    ),
    live_price: bool = Query(
        False,
        description="Whether to calculate the ranges using the current live price",
    ),
    historical: bool = Query(
        False,
        description="Whether to calculate the Historical Mandelbrot Channel",
    ),
    chart: bool = Query(False, description="Whether to include chart data"),
    template: Literal[
        "humbl_dark",
        "humbl_light",
        "ggplot2",
        "seaborn",
        "simple_white",
        "plotly",
        "plotly_white",
        "plotly_dark",
        "presentation",
        "xgridoff",
        "ygridoff",
        "gridon",
        "none",
    ] = Query(
        "humbl_dark", description="The Plotly template to use for charts"
    ),
):
    """
    Retrieve Mandelbrot Channel data for the specified symbols.

    This endpoint calculates the Mandelbrot Channel for the provided symbols
    using the Toolbox from humblDATA.

    Parameters
    ----------
    symbols : str, optional
        A comma-separated string of stock symbols. Default is "AAPL,NVDA,TSLA".

    interval : str, optional
        The interval for data points. Default is "1d".

    start_date : str, optional
        The start date for the data range. Default is "2000-01-01".

    end_date : str, optional
        The end date for the data range. Default is "2000-01-01".

    provider : str, optional
        The data provider to use. Default is "yfinance".

    window : str, optional
        The width of the window used for splitting the data into sections for detrending. Default is "1mo".

    rv_adjustment : bool, optional
        Whether to adjust the calculation for realized volatility. Default is True.

    rv_method : str, optional
        The method to calculate the realized volatility. Default is "std".

    rs_method : str, optional
        The method to use for Range/STD calculation. Default is "RS".

    rv_grouped_mean : bool, optional
        Whether to calculate the mean value of realized volatility over multiple window lengths. Default is False.

    live_price : bool, optional
        Whether to calculate the ranges using the current live price. Default is False.

    historical : bool, optional
        Whether to calculate the Historical Mandelbrot Channel. Default is False.

    chart : bool, optional
        Whether to include chart data. Default is False.

    template : str, optional
        The Plotly template to use for charts. Default is "humbl_dark".

    Returns
    -------
    dict
        A dictionary containing the Mandelbrot Channel data for the
        specified symbols.
    """
    try:
        symbol_list = validate_symbols(symbols.split(","))
        toolbox = Toolbox(
            symbols=symbol_list,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            provider=provider,
        )

        result = toolbox.technical.mandelbrot_channel(
            window=window,
            rv_adjustment=rv_adjustment,
            rv_method=rv_method,
            rs_method=rs_method,
            rv_grouped_mean=rv_grouped_mean,
            live_price=live_price,
            historical=historical,
            chart=chart,
            template=template,
        )

        if chart:
            json_data = result.to_json(chart=True)
            parsed_json = (
                orjson.loads(json_data)
                if isinstance(json_data, str)
                else [orjson.loads(item) for item in json_data]
            )
            return ORJSONResponse(content=parsed_json)
        else:
            return ORJSONResponse(
                content=result.to_dict(row_wise=True, as_series=False)
            )

    except Exception as e:
        error_message = f"Error in mandelbrot_channel_route: {e!s}"
        logger.exception(error_message)
        raise HTTPException(status_code=400, detail=error_message) from e

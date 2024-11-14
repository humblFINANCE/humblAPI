"""
humblCHANNEL API router.

This router is used to handle requests for the humblAPI humblCHANNEL <context>
"""

import datetime as dt
from typing import Any, Literal, TypeVar, Union

import orjson
import pytz
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import ORJSONResponse
from fastapi_cache.decorator import cache
from humbldata.toolbox.toolbox_controller import Toolbox
from pydantic import BaseModel, Field

from humblapi.core.config import config
from humblapi.core.logger import setup_logger
from humblapi.core.standard_models.abstract.responses import HumblResponse
from humblapi.core.utils import ORJsonCoder

router = APIRouter()
logger = setup_logger(name="humblapi.api.v1.routers.toolbox.humbl_channel")


class HumblChannelData(BaseModel):
    date: str | dt.datetime
    symbol: str
    bottom_price: float
    recent_price: float
    top_price: float


class HumblChannelResponse(BaseModel):
    data: list[HumblChannelData]


class PlotlyTrace(BaseModel):
    type: str
    x: list[str]
    y: list[float]
    name: str
    line: dict[str, Any] = Field(default_factory=dict)


class PlotlyLayout(BaseModel):
    title: dict[str, str]
    xaxis: dict[str, Any]
    yaxis: dict[str, Any]
    template: dict[str, Any] = Field(default_factory=dict)
    shapes: list[dict[str, Any]] = Field(default_factory=list)


class HumblChannelChartResponse(BaseModel):
    data: list[PlotlyTrace]
    layout: PlotlyLayout


class HumblChannelResult(BaseModel):
    result: HumblChannelResponse | HumblChannelChartResponse


def validate_symbols(symbols):
    if not symbols:
        msg = "No symbols provided"
        raise ValueError(msg)
    return symbols


@router.get(
    "/humblCHANNEL",
    response_class=ORJSONResponse,
    response_model=HumblResponse[
        Union[HumblChannelResponse, HumblChannelChartResponse]
    ],
)
@cache(expire=86000, namespace="humblCHANNEL", coder=ORJsonCoder)
async def humbl_channel_route(
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
) -> HumblResponse[Union[HumblChannelResponse, HumblChannelChartResponse]]:
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
        HumblChannelResponse: A response containing the Mandelbrot Channel data for the specified symbols.
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
            chart_response = HumblChannelChartResponse(**parsed_json[0])
            return HumblResponse[HumblChannelChartResponse](
                response_data=chart_response,
                status_code=200,
            )
        else:
            data = result.to_dict(row_wise=True, as_series=False)
            channel_response = HumblChannelResponse(
                data=[HumblChannelData(**item) for item in data]
            )
            return HumblResponse[HumblChannelResponse](
                response_data=channel_response,
                status_code=200,
            )

    except Exception as e:
        error_message = f"Error in humbl_channel_route: {e!s}"
        logger.exception(error_message)
        raise HTTPException(status_code=400, detail=error_message) from e

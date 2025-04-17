"""
humblCHANNEL API router.

This router is used to handle requests for the humblAPI humblCHANNEL <context>
"""

import datetime as dt
from typing import Literal

import orjson
import pytz
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import ORJSONResponse
from fastapi_cache.decorator import cache
from humbldata.toolbox.toolbox_controller import Toolbox
from pydantic import BaseModel

from humblapi.core.logger import setup_logger
from humblapi.core.standard_models.abstract.responses import HumblResponse
from humblapi.core.standard_models.plotly import (
    PlotlyLayout,
    PlotlyTrace,
)
from humblapi.core.utils import ORJsonCoder

router = APIRouter()
logger = setup_logger(name="humblapi.api.v1.routers.toolbox.humbl_channel")

# Constants
HUMBL_CHANNEL_QUERY_DESCRIPTIONS = {
    "symbols": "A comma-separated string of stock symbols",
    "interval": "The interval for data points",
    "start_date": "The start date for the data range",
    "end_date": "The end date for the data range",
    "provider": "The data provider to use",
    "window": "The width of the window used for splitting the data into sections for detrending",
    "rv_adjustment": "Whether to adjust the calculation for realized volatility",
    "rv_method": "The method to calculate the realized volatility",
    "rs_method": "The method to use for Range/STD calculation",
    "rv_grouped_mean": "Whether to calculate the mean value of realized volatility over multiple window lengths",
    "yesterday_close": "Whether to calculate the ranges using yesterday's closing price",
    "historical": "Whether to calculate the Historical Mandelbrot Channel",
    "chart": "Whether to include chart data",
    "template": "The Plotly template to use for charts",
    "membership": "The membership level of the user",
    "momentum": "Method to calculate momentum: 'shift' for simple shift, 'log' for logarithmic ROC, 'simple' for simple ROC",
    "equity_data": "Whether to include raw equity data in the response extra field",
}


class HumblChannelData(BaseModel):
    """Represents a row of humblCHANNEL data."""

    date: str | dt.datetime
    symbol: str
    bottom_price: float
    recent_price: float
    top_price: float


class HumblChannelResponse(BaseModel):
    """Represents the response structure for a humblCHANNEL response."""

    data: list[HumblChannelData]


class HumblChannelChartResponse(BaseModel):
    """Represents the response structure for a humblCHANNEL chart."""

    data: list[PlotlyTrace]
    layout: PlotlyLayout


class HumblChannelResult(BaseModel):
    """Represents the result of the humblCHANNEL API."""

    result: HumblChannelResponse | HumblChannelChartResponse


def validate_symbols(symbols):
    """Validate the symbols provided by the user."""
    if not symbols:
        msg = "No symbols provided"
        raise ValueError(msg)
    return symbols


@router.get(
    "/humblCHANNEL",
    response_class=ORJSONResponse,
    response_model=HumblResponse[
        HumblChannelResponse | HumblChannelChartResponse
    ],
)
@cache(expire=86000, namespace="humblCHANNEL", coder=ORJsonCoder)
async def humbl_channel_route(  # noqa: PLR0913
    symbols: str = Query(
        "AAPL,NVDA,TSLA",
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["symbols"],
    ),
    interval: str = Query(
        "1d",
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["interval"],
    ),
    start_date: str = Query(
        "2000-01-01",
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["start_date"],
    ),
    end_date: str = Query(
        default_factory=lambda: dt.datetime.now(
            tz=pytz.timezone("America/New_York")
        ).date(),
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["end_date"],
    ),
    provider: str = Query(
        "yfinance",
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["provider"],
    ),
    window: str = Query(
        "1mo",
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["window"],
    ),
    *,
    rv_adjustment: bool = Query(
        default=True,
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["rv_adjustment"],
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
        default="std",
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["rv_method"],
    ),
    rs_method: Literal["RS", "RS_min", "RS_max", "RS_mean"] = Query(
        default="RS",
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["rs_method"],
    ),
    rv_grouped_mean: bool = Query(
        default=False,
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["rv_grouped_mean"],
    ),
    yesterday_close: bool = Query(
        default=False,
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["yesterday_close"],
    ),
    historical: bool = Query(
        default=False,
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["historical"],
    ),
    chart: bool = Query(
        default=False,
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["chart"],
    ),
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
        "humbl_dark",
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["template"],
    ),
    momentum: Literal["shift", "log", "simple"] | None = Query(
        default=None,
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["momentum"],
    ),
    membership: Literal[
        "anonymous",
        "humblPEON",
        "humblPREMIUM",
        "humblPOWER",
        "humblPERMANENT",
        "admin",
    ] = Query(
        "anonymous",
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["membership"],
    ),
    equity_data: bool = Query(
        default=False,
        description=HUMBL_CHANNEL_QUERY_DESCRIPTIONS["equity_data"],
    ),
) -> HumblResponse[HumblChannelResponse | HumblChannelChartResponse]:
    """
    Retrieve Mandelbrot Channel data for the specified symbols.

    This endpoint calculates the Mandelbrot Channel for the provided symbols
    using the Toolbox from humblDATA.

    Parameters
    ----------
    membership : str, optional
        The membership level of the user. Default is "anonymous".

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

    yesterday_close : bool, optional
        Whether to calculate the ranges using yesterday's closing price. Default is False.

    historical : bool, optional
        Whether to calculate the Historical Mandelbrot Channel. Default is False.

    chart : bool, optional
        Whether to include chart data. Default is False.

    template : str, optional
        The Plotly template to use for charts. Default is "humbl_dark".

    membership : str, optional
        The membership level of the user. Default is "anonymous".

    equity_data : bool, optional
        Whether to include raw equity data in the response extra field. Default is False.

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
            membership=membership,
        )

        result = toolbox.technical.humbl_channel(
            window=window,
            rv_adjustment=rv_adjustment,
            rv_method=rv_method,
            rs_method=rs_method,
            rv_grouped_mean=rv_grouped_mean,
            yesterday_close=yesterday_close,
            historical=historical,
            chart=chart,
            template=template,
            momentum=momentum,
        )

        if chart:
            json_data = result.to_json(chart=True)
            parsed_json = (
                orjson.loads(json_data)
                if isinstance(json_data, str)
                else [orjson.loads(item) for item in json_data]
            )
            chart_response = HumblChannelChartResponse(**parsed_json[0])

            # Prepare extra equity data if requested
            if equity_data:
                extra_data = None
                try:
                    extra_data = result.to_polars(equity_data=True).select(
                        [
                            "date",
                            "close",
                        ]
                    )
                    extra_data = extra_data.to_dicts()
                except Exception as extra_exc:  # pragma: no cover
                    logger.warning(
                        "Failed to extract equity data for extra field: %s",
                        extra_exc,
                    )

            return HumblResponse(
                response_data=chart_response,
                message="humblCHANNEL data retrieved successfully with chart",
                status_code=200,
                warnings=result.warnings,
                extra=extra_data,
            )
        else:
            data = result.to_dict(row_wise=True, as_series=False)
            channel_response = HumblChannelResponse(
                data=[HumblChannelData(**item) for item in data]
            )

            # Prepare extra equity data if requested
            extra_data = None
            if equity_data:
                try:
                    extra_data = result.to_polars(equity_data=True).select(
                        [
                            "date",
                            "close",
                        ]
                    )
                    extra_data = extra_data.to_dicts()
                except Exception as extra_exc:  # pragma: no cover
                    logger.warning(
                        "Failed to extract equity data for extra field: %s",
                        extra_exc,
                    )

            return HumblResponse(
                response_data=channel_response,
                message="humblCHANNEL data retrieved successfully",
                status_code=200,
                warnings=result.warnings,
                extra=extra_data,
            )

    except Exception as e:
        error_message = f"Error in humbl_channel_route: {e!s}"
        logger.exception(error_message)
        raise HTTPException(status_code=400, detail=error_message) from e

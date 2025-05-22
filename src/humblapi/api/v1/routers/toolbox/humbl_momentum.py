"""
humblMOMENTUM API router.

This router is used to handle requests for the humblAPI humblMOMENTUM functionality.
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
logger = setup_logger(name="humblapi.api.v1.routers.toolbox.momentum")

# Constants
MOMENTUM_QUERY_DESCRIPTIONS = {
    "method": "Method to calculate momentum",
    "window": "Window to calculate momentum over",
    "chart": "Whether to return a chart object",
    "template": "The template/theme to use for the plotly figure",
}


class HumblMomentumData(BaseModel):
    """Represents a row of humblMOMENTUM data."""

    date: dt.date
    symbol: str
    close: float | None = None
    shifted: float | None = None
    momentum: float | None = None
    momentum_signal: int | None = None


class HumblMomentumChartResponse(BaseModel):
    """Represents the response structure for a humblMOMENTUM chart."""

    data: list[PlotlyTrace]
    layout: PlotlyLayout


class HumblMomentumResponse(BaseModel):
    """Represents the response structure for humblMOMENTUM data."""

    data: list[HumblMomentumData]


@router.get(
    "/humblMOMENTUM",
    response_class=ORJSONResponse,
    response_model=HumblResponse[
        HumblMomentumResponse | HumblMomentumChartResponse
    ],
)
@cache(
    expire=86400, namespace="humblMOMENTUM", coder=ORJsonCoder
)  # cached for a day
async def humbl_momentum_route(  # noqa: PLR0913
    symbols: str = Query(
        "AAPL",
        description="A comma-separated string of stock symbols",
    ),
    method: Literal["log", "simple", "shift"] = Query(
        "log",
        description=MOMENTUM_QUERY_DESCRIPTIONS["method"],
    ),
    window: str = Query(
        "1d",
        description=MOMENTUM_QUERY_DESCRIPTIONS["window"],
    ),
    *,
    chart: bool = Query(
        default=False,
        description=MOMENTUM_QUERY_DESCRIPTIONS["chart"],
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
        description=MOMENTUM_QUERY_DESCRIPTIONS["template"],
    ),
    start_date: str = Query(
        "2000-01-01", description="The start date for the data range"
    ),
    end_date: str | None = Query(
        default_factory=lambda: dt.datetime.now(
            tz=pytz.timezone("America/New_York")
        ).date(),
        description="The end date for the data range",
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
        description="The membership level of the user",
    ),
) -> HumblResponse[HumblMomentumResponse | HumblMomentumChartResponse]:
    """
    Retrieve humblMOMENTUM data for the specified parameters.

    This endpoint calculates momentum data using the Toolbox from humblDATA.

    Parameters are as described in the query parameters.

    Returns
    -------
    HumblResponse[Union[MomentumResponse, MomentumChartResponse]]
        A response containing the momentum data or chart based on the specified parameters.
    """
    try:
        toolbox = Toolbox(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            membership=membership,
        )

        result = await toolbox.technical.humbl_momentum(
            method=method,
            window=window,
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

            chart_response = HumblMomentumChartResponse(**parsed_json[0])
            return HumblResponse[
                HumblMomentumResponse | HumblMomentumChartResponse
            ](
                response_data=chart_response,
                status_code=200,
            )
        else:
            # Convert DataFrame to list of dicts and create MomentumData objects
            data = result.to_dict(row_wise=True, as_series=False)
            momentum_response = HumblMomentumResponse(
                data=[
                    HumblMomentumData(
                        **{k: v for k, v in item.items() if v is not None}
                    )
                    for item in data
                ]
            )
            return HumblResponse(
                response_data=momentum_response,
                message="humblMOMENTUM data retrieved successfully",
                status_code=200,
                warnings=result.warnings,
            )

    except Exception as e:
        error_message = f"Error in humbl_momentum_route: {e!s}"
        logger.exception(error_message)
        raise HTTPException(status_code=400, detail=error_message) from e

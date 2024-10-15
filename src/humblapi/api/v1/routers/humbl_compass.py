"""
HUMBL Compass API router.

This router is used to handle requests for the humblAPI HUMBL Compass functionality.
"""

import datetime as dt
from typing import Any, List, Literal, Optional, Union

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

router = APIRouter(
    prefix=config.API_V1_STR,
    tags=["toolbox"],
)
logger = setup_logger(name="humblapi.api.v1.routers.humbl_compass")


class HumblCompassData(BaseModel):
    """Represents the data structure for HUMBL Compass information."""

    date_month_start: str | dt.datetime
    country: str
    cpi: float
    cpi_3m_delta: float
    cpi_zscore: float | None = None
    cli: float
    cli_3m_delta: float
    cli_zscore: float | None = None


class HumblCompassResponse(BaseModel):
    """Represents the response structure for HUMBL Compass data."""

    data: list[HumblCompassData]


class PlotlyMarker(BaseModel):
    """Represents the marker properties for a Plotly trace."""

    color: list[int]
    colorscale: list[list[Any]]
    showscale: bool
    size: int


class PlotlyLine(BaseModel):
    """Represents the line properties for a Plotly trace."""

    color: str
    shape: str
    smoothing: float


class PlotlyTrace(BaseModel):
    """Represents a single trace in a Plotly chart."""

    hovertemplate: str
    line: PlotlyLine
    marker: PlotlyMarker
    mode: str
    name: str
    text: list[str]
    textfont: dict[str, Any]
    textposition: str
    x: list[float]
    y: list[float]
    type: str


class PlotlyShape(BaseModel):
    """Represents a shape in a Plotly chart layout."""

    fillcolor: str | None = None
    layer: str | None = None
    line: dict[str, Any]
    type: str
    x0: float | None = None
    x1: float | None = None
    y0: float | None = None
    y1: float | None = None
    xref: str | None = None
    yref: str | None = None


class PlotlyAxis(BaseModel):
    """Represents the properties of an axis in a Plotly chart."""

    title: dict[str, str]
    range: list[float]
    color: str
    showgrid: bool
    zeroline: bool


class PlotlyLayout(BaseModel):
    """Represents the layout properties of a Plotly chart."""

    template: dict[str, Any]
    shapes: list[PlotlyShape]
    title: dict[str, Any]
    xaxis: PlotlyAxis
    yaxis: PlotlyAxis
    font: dict[str, str]
    margin: dict[str, int]
    hovermode: str
    plot_bgcolor: str
    paper_bgcolor: str


class HumblCompassChartResponse(BaseModel):
    """Represents the response structure for a HUMBL Compass chart."""

    data: list[PlotlyTrace]
    layout: PlotlyLayout


@router.get(
    "/humbl-compass",
    response_class=ORJSONResponse,
    response_model=HumblResponse[
        Union[HumblCompassResponse, HumblCompassChartResponse]
    ],
)
@cache(
    expire=2629757, namespace="humbl_compass", coder=ORJsonCoder
)  # cached for a month
async def humbl_compass_route(
    country: Literal[
        "g20",
        "g7",
        "asia5",
        "north_america",
        "europe4",
        "australia",
        "brazil",
        "canada",
        "china",
        "france",
        "germany",
        "india",
        "indonesia",
        "italy",
        "japan",
        "mexico",
        "south_africa",
        "south_korea",
        "spain",
        "turkey",
        "united_kingdom",
        "united_states",
        "all",
    ] = Query(
        "united_states",
        description="The country or group of countries to collect humblCOMPASS data for",
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
    z_score: str | None = Query(
        None,
        description="The time window for z-score calculation (e.g., '1 year', '18 months')",
    ),
    chart: bool = Query(False, description="Whether to return a chart object"),
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
        description="The template/theme to use for the plotly figure",
    ),
) -> HumblResponse[HumblCompassResponse | HumblCompassChartResponse]:
    """
    Retrieve HUMBL Compass data for the specified country or group of countries.

    This endpoint calculates the HUMBL Compass data using the Toolbox from humblDATA.

    Parameters are as described in the query parameters.

    Returns
    -------
    HumblResponse[Union[HumblCompassResponse, HumblCompassChartResponse]]
        A response containing the HUMBL Compass data or chart for the specified country/countries.
    """
    try:
        toolbox = Toolbox(
            start_date=start_date,
            end_date=end_date,
        )

        result = toolbox.fundamental.humbl_compass(
            country=country,
            z_score=z_score,
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
            chart_response = HumblCompassChartResponse(**parsed_json[0])
            print(chart_response)
            return HumblResponse[HumblCompassChartResponse](
                response_data=chart_response,
                status_code=200,
            )
        else:
            data = result.to_dict(row_wise=True, as_series=False)
            compass_response = HumblCompassResponse(
                # remove None values from the data
                data=[
                    HumblCompassData(
                        **{k: v for k, v in item.items() if v is not None}
                    )
                    for item in data
                ]
            )
            return HumblResponse[HumblCompassResponse](
                response_data=compass_response,
                status_code=200,
            )

    except Exception as e:
        error_message = f"Error in humbl_compass_route: {e!s}"
        logger.exception(error_message)
        raise HTTPException(status_code=400, detail=error_message) from e

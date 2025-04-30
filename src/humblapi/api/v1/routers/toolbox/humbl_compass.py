"""
humblCOMPASS API router.

This router is used to handle requests for the humblAPI humblCOMPASS functionality.
"""

import datetime as dt
from typing import Literal

import orjson
import pytz
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import ORJSONResponse
from fastapi_cache.decorator import cache
from humbldata.core.standard_models.toolbox.fundamental.humbl_compass import (
    RegimeRecommendations,
)
from humbldata.toolbox.toolbox_controller import Toolbox
from pydantic import BaseModel, Field

from humblapi.core.logger import setup_logger
from humblapi.core.standard_models.abstract.responses import HumblResponse
from humblapi.core.standard_models.plotly import (
    PlotlyLayout,
    PlotlyTrace,
)
from humblapi.core.utils import ORJsonCoder

router = APIRouter()
logger = setup_logger(name="humblapi.api.v1.routers.toolbox.humbl_compass")

# Constants
HUMBL_COMPASS_QUERY_DESCRIPTIONS = {
    "country": "The country or group of countries to collect humblCOMPASS data for",
    "start_date": "The start date for the data range",
    "end_date": "The end date for the data range",
    "z_score": "The time window for z-score calculation (e.g., '1 year', '18 months')",
    "chart": "Whether to return a chart object",
    "template": "The template/theme to use for the plotly figure",
    "membership": "The membership level of the user",
    "recommendations": "Whether to include investment recommendations based on the HUMBL regime",
    "symbols": "A comma-separated string of stock symbols to backtest",
    "provider": "The data provider to use for backtesting (fmp or yfinance)",
}


class HumblCompassData(BaseModel):
    """Represents the data structure for humblCOMPASS information."""

    date_month_start: str | dt.datetime
    country: str
    cpi: float
    cpi_3m_delta: float
    cpi_zscore: float | None = None
    cli: float
    cli_3m_delta: float
    cli_zscore: float | None = None


class LatestHumblRegimeData(BaseModel):
    """Represents the latest regime data structure."""

    date: str
    humbl_regime: str


class HumblCompassChartResponse(BaseModel):
    """Represents the response structure for a humblCOMPASS chart."""

    data: list[PlotlyTrace]
    layout: PlotlyLayout
    latest_humbl_regime: LatestHumblRegimeData = Field(
        description="Latest humblREGIME data containing date and regime value"
    )
    recommendations: RegimeRecommendations | None = None


class HumblCompassResponse(BaseModel):
    """Represents the response structure for humblCOMPASS data."""

    data: list[HumblCompassData]
    recommendations: RegimeRecommendations | None = None
    latest_humbl_regime: LatestHumblRegimeData


class HumblCompassBacktestData(BaseModel):
    """Represents a row of humblCOMPASS backtest data."""

    symbol: str = Field(
        title="Symbol",
        description="The stock symbol being analyzed",
    )
    humbl_regime: str = Field(
        title="HUMBL Regime",
        description="The HUMBL regime classification (BOOM, BOUNCE, BLOAT, BUST)",
    )
    avg_total_return_pct: float = Field(
        title="Average Total Return %",
        description="Average total return percentage for each regime",
    )
    avg_ann_return_pct: float = Field(
        title="Average Annualized Return %",
        description="Average annualized return percentage for each regime",
    )
    avg_win_rate_pct: float = Field(
        title="Average Win Rate %",
        description="Average win rate (proportion of positive returns) for each regime",
    )
    avg_volatility: float = Field(
        title="Average Volatility",
        description="Average volatility percentage for each regime",
    )
    avg_sharpe_ratio: float = Field(
        title="Average Sharpe Ratio",
        description="Average Sharpe ratio for each regime",
    )
    avg_days_in_regime: float = Field(
        title="Average Days in Regime",
        description="Average number of days spent in each regime",
    )
    instance_count: int = Field(
        title="Instance Count",
        description="Number of occurrences of each regime",
    )
    cumulative_investment_growth: float = Field(
        title="Cumulative Investment Growth",
        description="Cumulative growth of the initial investment amount across all instances of each regime",
    )
    investment_growth_pct: float = Field(
        title="Investment Growth %",
        description="Percentage growth of investment relative to initial amount",
    )
    total_ending_investment_value: float = Field(
        title="Total Ending Investment Value",
        description="Total ending investment value including the initial investment amount",
    )
    total_win_count: int = Field(
        title="Total Win Count",
        description="Total number of days with positive returns across all instances",
    )
    total_loss_count: int = Field(
        title="Total Loss Count",
        description="Total number of days with negative returns across all instances",
    )
    avg_win_count_per_instance: float = Field(
        title="Avg Win Count Per Instance",
        description="Average number of days with positive returns per instance",
    )
    avg_loss_count_per_instance: float = Field(
        title="Avg Loss Count Per Instance",
        description="Average number of days with negative returns per instance",
    )
    min_return_pct: float = Field(
        title="Min Return %",
        description="Minimum return percentage across all instances of the regime",
    )
    max_return_pct: float = Field(
        title="Max Return %",
        description="Maximum return percentage across all instances of the regime",
    )
    max_win_days: int = Field(
        title="Max Win Days",
        description="Maximum number of win days in any instance of the regime",
    )
    min_win_days: int = Field(
        title="Min Win Days",
        description="Minimum number of win days in any instance of the regime",
    )
    max_loss_days: int = Field(
        title="Max Loss Days",
        description="Maximum number of loss days in any instance of the regime",
    )
    min_loss_days: int = Field(
        title="Min Loss Days",
        description="Minimum number of loss days in any instance of the regime",
    )
    max_drawdown_pct: float = Field(
        title="Max Drawdown %",
        description="Maximum drawdown percentage across all instances of the regime",
    )
    avg_drawdown_pct: float = Field(
        title="Avg Drawdown %",
        description="Average drawdown percentage across all instances of the regime",
    )
    avg_recovery_days: float = Field(
        title="Avg Recovery Days",
        description="Average number of days to recover from drawdowns",
    )
    max_recovery_days: int = Field(
        title="Max Recovery Days",
        description="Maximum number of days to recover from drawdowns",
    )


class HumblCompassBacktestResponse(BaseModel):
    """Represents the response structure for humblCOMPASS backtest data."""

    data: list[HumblCompassBacktestData]


class HumblCompassBacktestChartResponse(BaseModel):
    """Represents the response structure for a humblCOMPASS backtest chart."""

    data: list[PlotlyTrace]
    layout: PlotlyLayout


@router.get(
    "/humblCOMPASS",
    response_class=ORJSONResponse,
    response_model=HumblResponse[
        HumblCompassResponse | HumblCompassChartResponse
    ],
)
@cache(
    expire=2629757, namespace="humblCOMPASS", coder=ORJsonCoder
)  # cached for a month
async def humbl_compass_route(  # noqa: PLR0913
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
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["country"],
    ),
    start_date: str = Query(
        "2000-01-01",
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["start_date"],
    ),
    end_date: str | None = Query(
        default_factory=lambda: dt.datetime.now(
            tz=pytz.timezone("America/New_York")
        ).date(),
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["end_date"],
    ),
    z_score: str | None = Query(
        None,
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["z_score"],
    ),
    *,
    chart: bool = Query(
        default=False,
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["chart"],
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
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["template"],
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
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["membership"],
    ),
    recommendations: bool = Query(
        default=False,
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["recommendations"],
    ),
) -> HumblResponse[HumblCompassResponse | HumblCompassChartResponse]:
    """
    Retrieve humblCOMPASS data for the specified country or group of countries.

    This endpoint calculates the humblCOMPASS data using the Toolbox from humblDATA.

    Parameters are as described in the query parameters.

    Returns
    -------
    HumblResponse[Union[HumblCompassResponse, HumblCompassChartResponse]]
        A response containing the humblCOMPASS data or chart for the specified country/countries.
    """
    try:
        toolbox = Toolbox(
            start_date=start_date,
            end_date=end_date,
            membership=membership,
        )

        result = toolbox.fundamental.humbl_compass(
            country=country,
            z_score=z_score,
            chart=chart,
            template=template,
            recommendations=recommendations,
        )

        recommendations_data = (
            result.extra.get("humbl_regime_recommendations")
            if hasattr(result, "extra") and result.extra
            else None
        )

        # Get latest regime data - moved outside the if/else
        latest_data = (
            result.to_polars()
            .select(["date_month_start", "humbl_regime"])
            .row(-1)
        )
        latest_humbl_regime = LatestHumblRegimeData(
            date=latest_data[0].isoformat(),
            humbl_regime=latest_data[1],
        )

        if chart:
            json_data = result.to_json(chart=True)
            parsed_json = (
                orjson.loads(json_data)
                if isinstance(json_data, str)
                else [orjson.loads(item) for item in json_data]
            )

            chart_response = HumblCompassChartResponse(
                **parsed_json[0],
                latest_humbl_regime=latest_humbl_regime,
                recommendations=recommendations_data,
            )
            return HumblResponse[HumblCompassChartResponse](
                response_data=chart_response,
                status_code=200,
            )
        else:
            data = result.to_dict(row_wise=True, as_series=False)
            compass_response = HumblCompassResponse(
                data=[
                    HumblCompassData(
                        **{k: v for k, v in item.items() if v is not None}
                    )
                    for item in data
                ],
                latest_humbl_regime=latest_humbl_regime,
                recommendations=recommendations_data,
            )
            return HumblResponse[HumblCompassResponse](
                response_data=compass_response,
                status_code=200,
            )

    except Exception as e:
        error_message = f"Error in humbl_compass_route: {e!s}"
        logger.exception(error_message)
        raise HTTPException(status_code=400, detail=error_message) from e


@router.get(
    "/humblCOMPASS/backtest",
    response_class=ORJSONResponse,
    response_model=HumblResponse[
        HumblCompassBacktestResponse | HumblCompassBacktestChartResponse
    ],
)
@cache(
    expire=2629757, namespace="humblCOMPASS_backtest", coder=ORJsonCoder
)  # cached for a month
async def humbl_compass_backtest_route(  # noqa: PLR0913
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
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["country"],
    ),
    symbols: str = Query(
        "SPY,XLY,XLF",
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["symbols"],
    ),
    start_date: str = Query(
        "2000-01-01",
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["start_date"],
    ),
    end_date: str | None = Query(
        default_factory=lambda: dt.datetime.now(
            tz=pytz.timezone("America/New_York")
        ).date(),
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["end_date"],
    ),
    provider: Literal["fmp", "yfinance"] = Query(
        "yfinance",
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["provider"],
    ),
    *,
    chart: bool = Query(
        default=False,
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["chart"],
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
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["template"],
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
        description=HUMBL_COMPASS_QUERY_DESCRIPTIONS["membership"],
    ),
) -> HumblResponse[
    HumblCompassBacktestResponse | HumblCompassBacktestChartResponse
]:
    """
    Backtest trading strategies based on humblCOMPASS regimes for specified symbols.

    This endpoint performs backtesting using the humblCOMPASS data from humblDATA Toolbox.

    Parameters
    ----
    country : str
        The country or group of countries to collect humblCOMPASS data for.
    symbols : str
        A comma-separated string of stock symbols to backtest.
    start_date : str
        The start date for the backtest period.
    end_date : str, optional
        The end date for the backtest period.
    provider : str
        The data provider to use for backtesting (fmp or yfinance).
    chart : bool, optional
        Whether to return a chart object.
    template : str, optional
        The template/theme to use for the plotly figure.
    membership : str, optional
        The membership level of the user.

    Returns
    ----
    HumblResponse[Union[HumblCompassBacktestResponse, HumblCompassBacktestChartResponse]]
        A response containing the backtest data or chart for the specified symbols.
    """
    try:
        toolbox = Toolbox(
            start_date=start_date,
            end_date=end_date,
            membership=membership,
            provider=provider,
        )

        compass_result = toolbox.fundamental.humbl_compass(
            country=country,
            chart=chart,
            template=template,
        ).backtest(
            symbols=symbols.split(","),
            chart=chart,
        )
        if chart:
            json_data = compass_result.to_json(chart=True)
            parsed_json = (
                orjson.loads(json_data)
                if isinstance(json_data, str)
                else [orjson.loads(item) for item in json_data]
            )

            chart_response = HumblCompassBacktestChartResponse(**parsed_json[0])
            response: HumblResponse[
                HumblCompassBacktestResponse | HumblCompassBacktestChartResponse
            ] = HumblResponse(
                response_data=chart_response,
                status_code=200,
            )
            return response
        else:
            data = compass_result.to_dict(row_wise=True, as_series=False)
            backtest_response = HumblCompassBacktestResponse(
                data=[
                    HumblCompassBacktestData(
                        **{k: v for k, v in item.items() if v is not None}
                    )
                    for item in data
                ],
            )
            response: HumblResponse[
                HumblCompassBacktestResponse | HumblCompassBacktestChartResponse
            ] = HumblResponse(
                response_data=backtest_response,
                status_code=200,
            )
            return response

    except Exception as e:
        error_message = f"Error in humbl_compass_backtest_route: {e!s}"
        logger.exception(error_message)
        raise HTTPException(status_code=400, detail=error_message) from e

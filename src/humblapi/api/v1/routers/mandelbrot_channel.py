from fastapi import APIRouter, Query
from humbldata.toolbox.toolbox_controller import Toolbox

from humblapi.core.config import Config

config = Config()
router = APIRouter(
    prefix=config.API_V1_STR,
    tags=["mandelbrot_channel"],
)


@router.get("/mandelbrot-channel")
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
        "2000-01-01", description="The end date for the data range"
    ),
    window: str = Query("1m", description="The window size for calculations"),
    provider: str = Query("yfinance", description="The data provider to use"),
    historical: bool = Query(
        False, description="Whether to include historical data"
    ),
    boundary_group_down: bool = Query(
        False, description="Whether to group down the boundary"
    ),
    chart: bool = Query(False, description="Whether to include chart data"),
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
        The start date for the data range. Default is "2020-01-01".

    end_date : str, optional
        The end date for the data range. Default is "2020-08-01".

    historical : bool, optional
        Whether to include historical data. Default is False.

    window : str, optional
        The window size for calculations. Default is "1m".

    boundary_group_down : bool, optional
        Whether to group down the boundary. Default is False.

    provider : str, optional
        The data provider to use. Default is "yfinance".

    chart : bool, optional
        Whether to include chart data. Default is False.

    Returns
    -------
    dict
        A dictionary containing the Mandelbrot Channel data for the
        specified symbols.
    """
    symbol_list = symbols.split(",")

    toolbox = Toolbox(
        symbols=symbol_list,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        provider=provider,
    )

    result = toolbox.technical.mandelbrot_channel(
        historical=historical,
        window=window,
        _boundary_group_down=boundary_group_down,
        chart=chart,
    )

    return result.to_dict(row_wise=True, as_series=False)

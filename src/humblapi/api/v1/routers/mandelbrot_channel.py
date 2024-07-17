from fastapi import APIRouter
from humbldata.toolbox.toolbox_controller import Toolbox

from humblapi.core.config import Config

config = Config()
router = APIRouter(
    prefix=config.API_V1_STR,
    tags=["mandelbrot"],
)


@router.get("/mandelbrot-channel")
async def mandelbrot_channel_route(
    symbols: str = "PCT,AAPL,SNAP",
    interval: str = "1d",
    start_date: str = "2020-01-01",
    end_date: str = "2020-08-01",
    historical: bool = True,
    window: str = "1m",
    boundary_group_down: bool = False,
):
    """
    Retrieve Mandelbrot Channel data for the specified symbols.

    This endpoint calculates the Mandelbrot Channel for the provided symbols
    using the Toolbox from humblDATA.

    Parameters
    ----------
    symbols : str, optional
        A comma-separated string of stock symbols. Default is "PCT,AAPL,SNAP".
    interval : str, optional
        The interval for data points. Default is "1d".
    start_date : str, optional
        The start date for the data range. Default is "2020-01-01".
    end_date : str, optional
        The end date for the data range. Default is "2020-08-01".
    historical : bool, optional
        Whether to include historical data. Default is True.
    window : str, optional
        The window size for calculations. Default is "1m".
    boundary_group_down : bool, optional
        Whether to group down the boundary. Default is False.

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
    )

    result = toolbox.technical.mandelbrot_channel(
        historical=historical,
        window=window,
        _boundary_group_down=boundary_group_down,
    )

    return result.to_dict(row_wise=True, as_series=False)

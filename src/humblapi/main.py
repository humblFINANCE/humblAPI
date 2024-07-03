"""humblapi REST API."""

import logging
from contextlib import asynccontextmanager

import coloredlogs
from fastapi import FastAPI
from humbldata.portfolio.analytics.user_table.helpers import (
    aggregate_user_table_data,
)

from humblapi.api.v1.routers.user_table import user_table_route
from humblapi.core.config import Config


def fake_answer_to_everything_ml_model(x: float):
    return x * 42


ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application's lifecycle.

    This async context manager handles startup and shutdown events:
    - On startup: Load ML models and configure logging.
    - On shutdown: Clean up resources and clear ML models.

    The code before 'yield' runs at startup, after 'yield' at shutdown.
    """
    # Load the ML model
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers:
        logging.root.removeHandler(handler)
    # Add coloredlogs' coloured StreamHandler to the root logger.
    coloredlogs.install()
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


config = Config()
app = FastAPI(title=config.PROJECT_NAME, lifespan=lifespan)

# app.include_router(user_table_route)


@app.get("/")
def read_root() -> dict:
    """Read root."""
    return {"message": "Welcome to the humblapi API"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns
    -------
        dict: A JSON response indicating the API's health status and HTTP status code.
    """
    return {"data": {"message": "API is healthy"}, "status_code": 200}


@app.get("/predict")
async def predict(x: float):
    result = ml_models["answer_to_everything"](x)
    return {"result": result}


@app.get("/user-table")
async def user_table_route():
    """
    Retrieve user table data for specific symbols.

    This endpoint aggregates user table data for the specified symbols
    (XLU, XLE, and AAPL) using the aggregate_user_table_data function.
    The aggregated data is then collected and converted to a dictionary.

    Returns
    -------
    dict
        A dictionary containing the aggregated user table data for the
        specified symbols. The dict of a humblObject with `as_series=False` is
        identical to a JSON format.

    Notes
    -----
    The function uses the aggregate_user_table_data helper from the
    humbldata.portfolio.analytics.user_table.helpers module to perform
    the data aggregation.
    """
    user_table_data = (
        (await aggregate_user_table_data(symbols=["XLU", "XLE", "AAPL"]))
        .collect()
        .to_dict(as_series=False)
    )

    return user_table_data

"""humblapi REST API."""

import logging
from contextlib import asynccontextmanager

import coloredlogs
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from humblapi.api.v1.routers import user_table
from humblapi.core.config import Config
from humblapi.core.middleware import TimeLogMiddleware


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


# Setup App
config = Config()
app = FastAPI(title=config.PROJECT_NAME, lifespan=lifespan)

# Add Middleware
middleware = TimeLogMiddleware(some_attribute="some_attribute_here_if_needed")
app.add_middleware(BaseHTTPMiddleware, dispatch=middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add Routers
app.include_router(user_table.router)


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

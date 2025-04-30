"""Configuration module for the FastAPI application.

This module defines the configuration classes and settings for the FastAPI app.
It includes environment-specific configurations and utility functions to load
the appropriate configuration based on the current environment.
"""

import os

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Configuration class for the FastAPI application.

    This class defines the configuration settings for the application,
    including database connection details and API-related information.

    Attributes
    ----------
    DB_ENGINE : str | None
        The database engine to be used.
    DB_USERNAME : str | None
        The username for database connection.
    DB_PASS : str | None
        The password for database connection.
    DB_HOST : str | None
        The host address of the database.
    DB_PORT : str | None
        The port number for the database connection.
    DB_NAME : str | None
        The name of the database.
    API_V1_STR : str
        The base path for API version 1 endpoints.
    PROJECT_NAME : str
        The name of the project.
    REDIS_HOST : str
        The host address of the Redis server.
    REDIS_PORT : int
        The port number for the Redis connection.
    """

    PROJECT_NAME: str = "humblFINANCE FastAPI Backend"

    DB_ENGINE: str | None = os.getenv("DB_ENGINE", None)
    DB_USERNAME: str | None = os.getenv("DB_USERNAME", None)
    DB_PASS: str | None = os.getenv("DB_PASS", None)
    DB_HOST: str | None = os.getenv("DB_HOST", None)
    DB_PORT: str | None = os.getenv("DB_PORT", None)
    DB_NAME: str | None = os.getenv("DB_NAME", None)

    API_V1_STR: str = "/api/v1"

    FLUSH_API_TOKEN: str | None = os.getenv("FLUSH_API_TOKEN", None)
    OBB_PAT: str | None = os.getenv("OBB_PAT", None)


class ProductionConfig(Config):
    """
    Production configuration class.

    This class extends the base Config class and sets debug mode to False.

    Attributes
    ----------
    DEBUG : bool
        Flag to indicate whether debug mode is enabled (False for production).
    """

    DEBUG: bool = False
    DEVELOPMENT: bool = False

    REDIS_API_TOKEN: str | None = os.getenv("REDIS_API_TOKEN", None)
    REDIS_URL: str = f"rediss://default:{REDIS_API_TOKEN}@composed-bluegill-57562.upstash.io:6379"


class DevelopmentConfig(Config):
    """
    Development configuration class.

    This class extends the base Config class and sets debug mode to True.

    Attributes
    ----------
    DEBUG : bool
        Flag to indicate whether debug mode is enabled (True for development).
    """

    DEBUG: bool = True
    DEVELOPMENT: bool = True

    REDIS_URL: str = "redis://localhost"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379


def get_config():
    """
    Get the appropriate configuration based on the environment.

    This function determines the current environment and returns the
    corresponding configuration object.

    Returns
    -------
    Config
        The configuration object for the current environment.
    """
    env = os.getenv("ENV", "dev")
    config_type = {
        "dev": DevelopmentConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config | DevelopmentConfig | ProductionConfig = get_config()

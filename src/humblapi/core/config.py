"""Configuration module for the FastAPI application.

This module defines the configuration classes and settings for the FastAPI app.
It includes environment-specific configurations and utility functions to load
the appropriate configuration based on the current environment.
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    """

    DB_ENGINE: str | None = os.getenv("DB_ENGINE", None)
    DB_USERNAME: str | None = os.getenv("DB_USERNAME", None)
    DB_PASS: str | None = os.getenv("DB_PASS", None)
    DB_HOST: str | None = os.getenv("DB_HOST", None)
    DB_PORT: str | None = os.getenv("DB_PORT", None)
    DB_NAME: str | None = os.getenv("DB_NAME", None)

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "humblFINANCE FastAPI Backend"


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


def get_config():
    """
    Get the appropriate configuration based on the environment.

    This function determines the current environment and returns the
    corresponding configuration object.

    Returns
    -------
    Config
        The configuration object for the current environment.

    Notes
    -----
    The function prints the DB_ENGINE value for debugging purposes.
    """
    print(os.getenv("DB_ENGINE", None))
    env = os.getenv("ENV", "test")
    config_type = {
        "test": DevelopmentConfig(),
        "prod": ProductionConfig(),
    }
    print(config_type["test"].DB_ENGINE)
    return config_type[env]


config: Config = get_config()

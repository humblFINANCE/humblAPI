import os
from pathlib import Path
from typing import Dict, Optional

import dotenv

from humblapi.core.standard_models.abstract.singleton import SingletonMeta


class Env(metaclass=SingletonMeta):
    """Environment variables."""

    _environ: dict[str, str]

    def __init__(self) -> None:
        env_path = dotenv.find_dotenv()
        dotenv.load_dotenv(Path(env_path))

        self._environ = os.environ.copy()

    @property
    def SERVICE_API(self) -> str | None:  # noqa: N802
        """Example API KEY."""
        return self._environ.get("SERVICE_API", None)

    @property
    def LOGGER_LEVEL(self) -> int:
        """
        Get the global logger level.

        Returns
        -------
        int
            The numeric logging level (default: 20 for INFO).

        Notes
        -----
        Mapping of string levels to numeric values:
        DEBUG: 10, INFO: 20, WARNING: 30, ERROR: 40, CRITICAL: 50
        """
        level_map = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50,
        }
        return level_map.get(
            self._environ.get("LOGGER_LEVEL", "INFO").upper(), 20
        )

    @property
    def ENVIRONMENT(self) -> str:  # noqa: N802
        """Get the current API environment (development or production)."""
        return self._environ.get("ENVIRONMENT", "development").lower()

    @property
    def ENV(self) -> str:
        """
        Alias for ENVIRONMENT property.

        Returns
        -------
        str
            The environment; either 'development' or 'production'.
        """
        return (
            "development" if self.ENVIRONMENT == "development" else "production"
        )

    @property
    def DEVELOPMENT(self) -> bool:
        """
        Check if the environment is development.

        Returns
        -------
        bool
            True if the environment is development, False otherwise.
        """
        return self.ENV.lower() == "development"

    @property
    def OPENBB_API_PROD_URL(self) -> str | None:  # noqa: N802
        """OpenBB External API Production URL (root)."""
        return self._environ.get("OPENBB_API_PROD_URL")

    @property
    def OPENBB_API_DEV_URL(self) -> str | None:  # noqa: N802
        """OpenBB External API Development URL (root)."""
        return self._environ.get("OPENBB_API_DEV_URL")

    @property
    def OPENBB_API_PREFIX(self) -> str:  # noqa: N802
        """OpenBB API Prefix."""
        return self._environ.get("OPENBB_API_PREFIX", "/api/v1")

    @property
    def OBB_PAT(self) -> str | None:  # noqa: N802
        """OpenBB Personal Access Token."""
        return self._environ.get("OBB_PAT", None)

    @property
    def OBB_LOGGED_IN(self) -> bool:
        return self.str2bool(self._environ.get("OBB_LOGGED_IN", False))

    @property
    def REDIS_REST_API_READ_ONLY_TOKEN(self) -> str | None:
        """Redis REST API read-only token."""
        return self._environ.get("REDIS_REST_API_READ_ONLY_TOKEN", None)

    @property
    def REDIS_API_TOKEN(self) -> str | None:
        """Redis API token."""
        return self._environ.get("REDIS_API_TOKEN", None)

    @property
    def REDIS_REST_API_URL(self) -> str | None:
        """Redis REST API URL."""
        return self._environ.get("REDIS_REST_API_URL", None)

    @property
    def REDIS_URL(self) -> str | None:
        """Redis URL."""
        return self._environ.get("REDIS_URL", None)

    @staticmethod
    def str2bool(value: str | bool) -> bool:
        """Match a value to its boolean correspondent.

        Args:
            value (str): The string value to be converted to a boolean.

        Returns
        -------
            bool: The boolean value corresponding to the input string.

        Raises
        ------
            ValueError: If the input string does not correspond to a boolean
            value.
        """
        if isinstance(value, bool):
            return value
        if value.lower() in {"false", "f", "0", "no", "n"}:
            return False
        if value.lower() in {"true", "t", "1", "yes", "y"}:
            return True
        msg = f"Failed to cast '{value}' to bool."
        raise ValueError(msg)

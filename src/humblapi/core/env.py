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

    # Use this when you want a variable to return a bool
    @staticmethod
    def str2bool(value) -> bool:
        """Match a value to its boolean correspondent."""
        if isinstance(value, bool):
            return value
        if value.lower() in {"false", "f", "0", "no", "n"}:
            return False
        if value.lower() in {"true", "t", "1", "yes", "y"}:
            return True
        msg = f"Failed to cast {value} to bool."
        raise ValueError(msg)

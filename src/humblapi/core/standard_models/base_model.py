import dataclasses as dc
from typing import Any, Dict, Optional

# pandera >=0.24 deprecates the top-level pandas-specific re-exports in
# favor of the explicit `pandera.pandas` module - see
# https://pandera.readthedocs.io/en/stable/supported_libraries.html
import pandera.pandas as pa


# The generic type of a single row in given Relation.
# Should be a typed subclass of Model.
class PanderaBase(pa.DataFrameModel):
    def __repr__(self) -> str:
        """Return string representation of model."""
        dataclass_repr = ""
        for key, value in sorted(self.__dict__.items()):
            if key.startswith("_"):
                continue
            dataclass_repr += f"    {key}='{value}', \n"

        return f"{self.__class__.__name__}(\n{dataclass_repr[:-2]}\n)"

    @classmethod
    def get_fields(cls) -> dict[str, Any]:
        """Get dict of fields."""
        return cls.__fields__  # type: ignore

    def get_value(self, field: str) -> Any | None:
        """Get field value."""
        if hasattr(self, field):
            return getattr(self, field)
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dict."""
        return dc.asdict(self)  # type: ignore

    def get_default(self, field: str) -> Any | None:
        """Get default field value."""
        if hasattr(self, field):
            return self.get_fields()[field].default
        return None

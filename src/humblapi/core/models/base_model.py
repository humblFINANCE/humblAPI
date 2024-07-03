import dataclasses as dc
from typing import Any, Dict, Optional

import pandera as pa


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
    def get_fields(cls) -> Dict[str, Any]:
        """Get dict of fields."""
        return cls.__fields__  # type: ignore

    def get_value(self, field: str) -> Optional[Any]:
        """Get field value."""
        if hasattr(self, field):
            return getattr(self, field)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dict."""
        return dc.asdict(self)  # type: ignore

    def get_default(self, field: str) -> Optional[Any]:
        """Get default field value."""
        if hasattr(self, field):
            return self.get_fields()[field].default
        return None

from enum import Enum
from typing import Any


def validate_enum(v: Any) -> Any:
    if v is not None and isinstance(v, Enum):
        return v.value
    return v

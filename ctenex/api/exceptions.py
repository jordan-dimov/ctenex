from typing import Any, Dict, Optional

from fastapi import HTTPException

# HTTP exceptions (meant to stop execution on the spot)


class CTMDSException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

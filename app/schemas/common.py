from pydantic import BaseModel
from typing import Optional, Any


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    data: Optional[Any] = None

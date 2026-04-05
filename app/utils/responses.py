from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """
    Every endpoint returns this shape:
    {
        "success": true,
        "message": "Incidents retrieved",
        "data": { ... }
    }
    """

    success: bool
    message: str
    data: Optional[T] = None


def success_response(data: Any = None, message: str = "Success") -> dict:
    return {"success": True, "message": message, "data": data}


def error_response(message: str) -> dict:
    return {"success": False, "message": message, "data": None}

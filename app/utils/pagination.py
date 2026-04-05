from typing import TypeVar, Generic, List
from pydantic import BaseModel
from fastapi import Query

T = TypeVar("T")


class PaginationParams:
    """
    Usage in endpoint:
        def list_incidents(pagination: PaginationDep):
    """

    def __init__(
        self,
        page: int = Query(default=1, ge=1, description="Page number"),
        page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


from typing import Annotated
from fastapi import Depends

PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response shape — use this everywhere"""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[T], total: int, pagination: PaginationParams):
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=(total + pagination.page_size - 1) // pagination.page_size,
        )

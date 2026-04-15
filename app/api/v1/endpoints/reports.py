from fastapi import APIRouter
from uuid import UUID
from typing import Optional

from app.core.dependencies import DB, ModeratorOrAdmin
from app.utils.pagination import PaginationDep, PaginatedResponse
from app.utils.responses import success_response
from app.models.report import ReportCategory, ReportStatus
from app.schemas.reports import ReportOut
import app.services.reports as service

router = APIRouter()


@router.get("/", dependencies= [ModeratorOrAdmin])
def list_reports(
    db: DB,
    pagination: PaginationDep,
    status: Optional[ReportStatus] = None,
    category: Optional[ReportCategory] = None,
    author_id: Optional[UUID] = None,
    
):
    reports, total = service.list_reports(
        db, pagination, status, category, author_id
    )

    return success_response(
        data={
            "items": [ReportOut.model_validate(r).model_dump() for r in reports],
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
        },
        message="Reports retrieved"
    )
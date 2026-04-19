from fastapi import APIRouter, status
from uuid import UUID
from typing import Optional

from app.core.dependencies import DB, ModeratorOrAdmin, AdminOnly
from app.utils.pagination import PaginationDep, PaginatedResponse
from app.utils.responses import success_response
from app.models.report import ReportCategory, ReportStatus
from app.schemas.reports import ReportCreateOut, ReportOut, ReportCreate
import app.services.reports as service
from app.core.dependencies import DB, ModeratorOrAdmin, CurrentUser

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

@router.get("/{id}")
def get_report(
    id: UUID,
    db: DB,
):
    report = service.get_report_by_id(db, id)
    
    return success_response(
        data=ReportOut.model_validate(report).model_dump(),
        message="Report retrieved"
    )

@router.post("/")
def submit_report(
    payload: ReportCreate,
    db: DB,
    current_user: CurrentUser,
):
    report, potential_duplicate_of = service.create_report(db, current_user.id, payload)

    return success_response(
        data=ReportCreateOut(
            **ReportOut.model_validate(report).model_dump(),
            potential_duplicate_of=potential_duplicate_of
        ).model_dump(),
        message="Report submitted successfully"
    )

@router.delete("/{report_id}", dependencies=[AdminOnly], status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: UUID, db: DB):
    service.delete_report(db, report_id)


    

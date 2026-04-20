from fastapi import APIRouter, status
from uuid import UUID
from typing import Optional

from app.core.dependencies import DB, ModeratorOrAdmin, AdminOnly
from app.utils.pagination import PaginationDep, PaginatedResponse
from app.utils.responses import success_response
from app.models.report import ReportCategory, ReportStatus
from app.schemas.reports import (
    ReportCreateOut,
    ReportOut,
    ReportCreate,
    ReportReject,
    ReportMarkDuplicate,
    VoteCreate,
    VoteOut,
    ModerationLogOut,
)
import app.services.reports as service
from app.core.dependencies import DB, ModeratorOrAdmin, CurrentUser

router = APIRouter()
moderation_router = APIRouter()


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


@router.patch("/{report_id}/approve", dependencies=[ModeratorOrAdmin])
def approve_report(report_id: UUID, db: DB, current_user: CurrentUser):
    report = service.approve_report(db, report_id, current_user.id)
    return success_response(
        data=ReportOut.model_validate(report).model_dump(),
        message="Report approved successfully"
    )

@router.patch("/{report_id}/reject", dependencies=[ModeratorOrAdmin])
def reject_report(report_id: UUID, payload: ReportReject, db: DB, current_user: CurrentUser):
    report = service.reject_report(db, report_id, current_user.id, payload.reason)
    return success_response(
        data=ReportOut.model_validate(report).model_dump(),
        message="Report rejected successfully"
    )
    

@router.patch("/{report_id}/mark-duplicate", dependencies=[ModeratorOrAdmin])
def mark_report_duplicate(
    report_id: UUID,
    payload: ReportMarkDuplicate,
    db: DB,
    current_user: CurrentUser,
):
    report = service.mark_report_duplicate(
        db,
        report_id,
        payload.duplicate_of,
        current_user.id,
    )
    return success_response(
        data=ReportOut.model_validate(report).model_dump(),
        message="Report marked as duplicate successfully"
    )


@router.post("/{report_id}/vote", status_code=status.HTTP_201_CREATED)
def vote_on_report(
    report_id: UUID,
    payload: VoteCreate,
    db: DB,
    current_user: CurrentUser,
):
    vote, report = service.vote_report(db, report_id, current_user.id, payload.is_upvote)
    return success_response(
        data=VoteOut(
            **{
                "id": vote.id,
                "report_id": vote.report_id,
                "user_id": vote.user_id,
                "is_upvote": vote.is_upvote,
                "created_at": vote.created_at,
                "confidence_score": report.confidence_score,
            }
        ).model_dump(),
        message="Vote cast successfully",
    )


@moderation_router.get("/logs", dependencies=[AdminOnly])
def list_moderation_logs(
    db: DB,
    pagination: PaginationDep,
):
    logs, total = service.list_moderation_logs(db, pagination)

    return success_response(
        data={
            "items": [ModerationLogOut.model_validate(log).model_dump() for log in logs],
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
        },
        message="Moderation logs retrieved",
    )

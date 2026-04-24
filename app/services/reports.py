from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.reports import ReportCreate
from app.models.report import Report, ReportCategory, ReportStatus, ModerationLog, ReportVote
from fastapi import HTTPException
from app.utils.geo import haversine_distance


def list_reports(
    db: Session,
    pagination,
    status: Optional[ReportStatus] = None,
    category: Optional[ReportCategory] = None,
    author_id: Optional[UUID] = None,
):
    query = db.query(Report)

    if status is not None:
        query = query.filter(Report.status == status)

    if category is not None:
        query = query.filter(Report.category == category)

    if author_id is not None:
        query = query.filter(Report.author_id == author_id)

    query = query.order_by(Report.created_at.desc())

    total = query.count()
    reports = query.offset(pagination.offset).limit(pagination.page_size).all()

    return reports, total



def get_report_by_id(db: Session, report_id: UUID):
    # Raw SQL existence check
    row = db.execute(
        text("SELECT id FROM reports WHERE id = :id"),
        {"id": str(report_id)}
    ).first()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    # Reload as ORM object so relationships and Pydantic serialisation work
    return db.query(Report).filter(Report.id == report_id).first()

def check_abuse(db: Session, user_id: UUID) -> bool:
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

    recent_count = db.query(Report).filter(
        Report.author_id == user_id,
        Report.created_at >= one_hour_ago
    ).count()

    return recent_count >= 10


def detect_duplicate(
    db: Session,
    category: ReportCategory,
    latitude: float,
    longitude: float,
) -> Report | None:
    two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
    lat_delta = 0.0045
    lng_delta = 0.0045

    candidates = db.query(Report).filter(
        Report.category == category,
        Report.created_at >= two_hours_ago,
        Report.status != ReportStatus.rejected,
        Report.latitude.between(latitude - lat_delta, latitude + lat_delta),
        Report.longitude.between(longitude - lng_delta, longitude + lng_delta),
    ).all()

    for report in candidates:
        if haversine_distance(latitude, longitude, report.latitude, report.longitude) <= 0.5:
            return report

    return None


def create_report(db: Session, user_id: UUID, payload: ReportCreate):
    if check_abuse(db, user_id):
        raise HTTPException(status_code=429, detail="Too many reports submitted in the last hour")

    potential_duplicate = detect_duplicate(
        db,
        payload.category,
        payload.latitude,
        payload.longitude
    )

    report = Report(
        author_id=user_id,
        category=payload.category,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        status=ReportStatus.pending,
        confidence_score=0,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report, (potential_duplicate.id if potential_duplicate else None)

def delete_report(db: Session, report_id: UUID):
    report = get_report_by_id(db, report_id)
    db.query(Report).filter(Report.duplicate_of == report_id).update({"duplicate_of": None})
    db.query(ModerationLog).filter(ModerationLog.report_id == report_id).update({"report_id": None})
    db.delete(report)
    db.commit()
    return True


def approve_report(db: Session, report_id: UUID, moderator_id: UUID):
    report = get_report_by_id(db, report_id)

    if report.status != ReportStatus.pending:
        raise HTTPException(status_code=400, detail="only pending reports can be approved")
    
    report.status = ReportStatus.approved
    db.add(report)
    db.add(ModerationLog(
    moderator_id=moderator_id,
    report_id=report.id,
    action="approved",
    ))
    db.commit()
    db.refresh(report)
    return report

def reject_report(db: Session, report_id: UUID, moderator_id: UUID, reason: str):
    report = get_report_by_id(db, report_id)

    if report.status != ReportStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending reports can be rejected")

    report.status = ReportStatus.rejected
    db.add(report)
    db.add(ModerationLog(
        moderator_id=moderator_id,
        report_id=report.id,
        action="rejected",
        reason=reason,
    ))
    db.commit()
    db.refresh(report)
    return report


def mark_report_duplicate(
    db: Session,
    report_id: UUID,
    duplicate_of_id: UUID,
    moderator_id: UUID,
):
    report = get_report_by_id(db, report_id)
    original_report = get_report_by_id(db, duplicate_of_id)

    if report.id == original_report.id:
        raise HTTPException(
            status_code=400,
            detail="A report cannot be marked as a duplicate of itself",
        )

    if report.status != ReportStatus.pending:
        raise HTTPException(
            status_code=400,
            detail="Only pending reports can be marked as duplicate",
        )

    if original_report.status == ReportStatus.rejected:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark a report as duplicate of a rejected report",
        )

    report.status = ReportStatus.duplicate
    report.duplicate_of = original_report.id
    db.add(report)
    db.add(
        ModerationLog(
            moderator_id=moderator_id,
            report_id=report.id,
            action="marked_duplicate",
        )
    )
    db.commit()
    db.refresh(report)
    return report


def vote_report(db: Session, report_id: UUID, user_id: UUID, is_upvote: bool):
    report = get_report_by_id(db, report_id)

    # Prevent authors from voting on their own report
    if report.author_id == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot vote on your own report",
        )

    existing_vote = (
        db.query(ReportVote)
        .filter(ReportVote.report_id == report_id, ReportVote.user_id == user_id)
        .first()
    )

    if existing_vote:
        if existing_vote.is_upvote == is_upvote:
            raise HTTPException(
                status_code=409,
                detail="You have already cast this vote on the report",
            )
        # Flip the vote: reverse the previous contribution and apply the new one
        delta = 2 if is_upvote else -2
        existing_vote.is_upvote = is_upvote
        report.confidence_score += delta
        db.add(existing_vote)
    else:
        vote = ReportVote(
            report_id=report_id,
            user_id=user_id,
            is_upvote=is_upvote,
        )
        report.confidence_score += 1 if is_upvote else -1
        db.add(vote)
        existing_vote = vote

    db.add(report)
    db.commit()
    db.refresh(existing_vote)
    db.refresh(report)

    return existing_vote, report


def list_moderation_logs(db: Session, pagination):
    # Raw SQL count
    total = db.execute(
        text("SELECT COUNT(*) FROM moderation_logs")
    ).scalar()

    # Raw SQL paginated fetch
    rows = db.execute(
        text("""
            SELECT id FROM moderation_logs
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """),
        {"limit": pagination.page_size, "offset": pagination.offset},
    ).mappings().all()

    # Reload as ORM objects to keep Pydantic serialisation clean
    ids = [row["id"] for row in rows]
    if not ids:
        return [], total

    logs = db.query(ModerationLog).filter(ModerationLog.id.in_(ids)).all()
    # Restore ORDER BY ordering lost by IN query
    id_index = {str(log.id): i for i, log in enumerate(logs)}
    logs.sort(key=lambda log: [str(r["id"]) for r in rows].index(str(log.id)))

    return logs, total

from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.schemas.reports import ReportCreate
from app.models.report import Report, ReportCategory, ReportStatus
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
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report

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

    recent_reports = db.query(Report).filter(
        Report.category == category,
        Report.created_at >= two_hours_ago,
        Report.status != ReportStatus.rejected
    ).all()

    for report in recent_reports:
        distance = haversine_distance(
            latitude,
            longitude,
            report.latitude,
            report.longitude
        )
        if distance <= 0.5:
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

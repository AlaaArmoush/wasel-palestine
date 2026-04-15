from sqlalchemy.orm import Session
from app.models.report import Report, ReportCategory, ReportStatus

def list_reports(db: Session, pagination, status, category, author_id):
    query = db.query(Report)

    if status:
        query = query.filter(Report.status == status)
    if category:
        query = query.filter(Report.category == category)
    if author_id:
        query = query.filter(Report.author_id == author_id)

    total = query.count()
    reports = query.offset(pagination.offset).limit(pagination.page_size).all()

    return reports, total
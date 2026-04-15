from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.checkpoint import Checkpoint, CheckpointStatus

def get_checkpoints(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: str | None = None,
    status: CheckpointStatus | None = None,
    is_active: bool | None = None,
):
    query = db.query(Checkpoint)
    
    if name:
        query = query.filter(
            (Checkpoint.name.ilike(f"%{name}%")) | 
            (Checkpoint.name_ar.ilike(f"%{name}%"))
        )
    
    if status is not None:
        query = query.filter(Checkpoint.current_status == status)
        
    if is_active is not None:
        query = query.filter(Checkpoint.is_active == is_active)
        
    total = query.count()
    items = query.order_by(Checkpoint.created_at.desc()).offset(skip).limit(limit).all()
    
    return items, total


def get_checkpoint_by_id(db: Session, checkpoint_id: UUID):
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()
    if not checkpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Checkpoint not found"
        )
    return checkpoint

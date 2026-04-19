from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.checkpoint import Checkpoint, CheckpointStatus, CheckpointStatusHistory
from app.schemas.checkpoint import CheckpointCreate, CheckpointUpdate

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


def get_checkpoint_history(
    db: Session,
    checkpoint_id: UUID,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(CheckpointStatusHistory).filter(CheckpointStatusHistory.checkpoint_id == checkpoint_id)
    total = query.count()
    items = query.order_by(CheckpointStatusHistory.changed_at.desc()).offset(skip).limit(limit).all()
    
    return items, total













#for post method
def create_checkpoint(db: Session, obj_in: CheckpointCreate, current_user_id: UUID | None = None):
    db_obj = Checkpoint(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    history = CheckpointStatusHistory(
        checkpoint_id=db_obj.id,
        new_status=db_obj.current_status,
        changed_by=current_user_id,
        reason="Initial creation"
    )
    db.add(history)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj


def update_checkpoint(db: Session, checkpoint_id: UUID, obj_in: CheckpointUpdate, current_user_id: UUID | None = None):
    checkpoint = get_checkpoint_by_id(db, checkpoint_id)
    
    update_data = obj_in.model_dump(exclude_unset=True)
    if not update_data:
        return checkpoint
        
    status_changed = False
    old_status = checkpoint.current_status
    
    if "current_status" in update_data and update_data["current_status"] != checkpoint.current_status:
        status_changed = True
        
    for field, value in update_data.items():
        setattr(checkpoint, field, value)
        
    db.add(checkpoint)
    
    if status_changed:
        history = CheckpointStatusHistory(
            checkpoint_id=checkpoint.id,
            previous_status=old_status,
            new_status=checkpoint.current_status,
            changed_by=current_user_id,
            reason="Admin update"
        )
        db.add(history)
        
    db.commit()
    db.refresh(checkpoint)
    
    return checkpoint


def delete_checkpoint(db: Session, checkpoint_id: UUID):
    checkpoint = get_checkpoint_by_id(db, checkpoint_id)
    db.delete(checkpoint)
    db.commit()
    return True

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.data_conflict import DataConflict
from app.schemas.conflict import ConflictRead, ConflictResolveRequest
from app.services.conflict_service import get_conflict, list_conflicts, resolve_conflict

router = APIRouter(prefix="/conflicts", tags=["conflicts"])


@router.get("", response_model=list[ConflictRead])
def conflicts(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[DataConflict]:
    return list_conflicts(db)


@router.get("/{conflict_id}", response_model=ConflictRead)
def conflict(conflict_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> DataConflict:
    conflict = get_conflict(db, conflict_id)
    if not conflict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conflict not found")
    return conflict


@router.post("/{conflict_id}/resolve", response_model=ConflictRead)
def resolve(conflict_id: str, payload: ConflictResolveRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> DataConflict:
    conflict = resolve_conflict(db, conflict_id, resolved_value=payload.resolved_value, resolved_by=current_user.email, status=payload.status)
    if not conflict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conflict not found")
    return conflict


@router.post("/{conflict_id}/ignore", response_model=ConflictRead)
def ignore(conflict_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> DataConflict:
    conflict = resolve_conflict(db, conflict_id, resolved_value=None, resolved_by=current_user.email, status="IGNORED")
    if not conflict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conflict not found")
    return conflict

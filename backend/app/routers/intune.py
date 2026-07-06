from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.sync_run import SyncRun
from app.schemas.intune import IntuneSyncRequest, SyncRunRead
from app.services.intune_sync_service import sync_intune_devices

router = APIRouter(prefix="/sync/intune", tags=["intune"])


@router.post("", response_model=SyncRunRead)
def sync_intune(payload: IntuneSyncRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> SyncRun:
    try:
        return sync_intune_devices(db, bearer_token=payload.bearer_token, graph_url=payload.graph_url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/history", response_model=list[SyncRunRead])
def history(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[SyncRun]:
    return list(db.scalars(select(SyncRun).order_by(SyncRun.created_at.desc())))


@router.get("/{sync_run_id}", response_model=SyncRunRead)
def get_sync_run(sync_run_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> SyncRun:
    run = db.get(SyncRun, sync_run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sync run not found")
    return run

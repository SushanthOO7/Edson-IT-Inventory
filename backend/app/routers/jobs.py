from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.import_run import ImportRun
from app.models.sync_run import SyncRun

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _import_job(run: ImportRun) -> dict[str, str | int | None]:
    return {
        "job_id": run.id,
        "kind": "servicenow-import",
        "source": run.source,
        "status": run.status,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "total_records": run.total_rows,
        "matched_devices": run.matched_devices,
        "created_devices": run.created_devices,
        "conflicts_created": run.conflicts_created,
        "errors_count": run.errors_count,
        "label": run.email_subject or run.file_name or run.source,
    }


def _sync_job(run: SyncRun) -> dict[str, str | int | None]:
    return {
        "job_id": run.id,
        "kind": "intune-sync",
        "source": run.source,
        "status": run.status,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "total_records": run.total_records,
        "matched_devices": run.matched_devices,
        "created_devices": run.created_devices,
        "conflicts_created": run.conflicts_created,
        "errors_count": run.errors_count,
        "label": run.source,
    }


@router.get("")
def list_jobs(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, list[dict[str, str | int | None]]]:
    import_jobs = [_import_job(run) for run in db.scalars(select(ImportRun).order_by(ImportRun.created_at.desc()).limit(25))]
    sync_jobs = [_sync_job(run) for run in db.scalars(select(SyncRun).order_by(SyncRun.created_at.desc()).limit(25))]
    items = sorted(import_jobs + sync_jobs, key=lambda item: str(item.get("created_at") or ""), reverse=True)
    return {"items": items}


@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, str | int | dict | None]:
    import_run = db.get(ImportRun, job_id)
    if import_run:
        job = _import_job(import_run)
        job["error_log"] = import_run.error_log
        return job

    sync_run = db.get(SyncRun, job_id)
    if sync_run:
        job = _sync_job(sync_run)
        job["error_log"] = sync_run.error_log
        return job

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

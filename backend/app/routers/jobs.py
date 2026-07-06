from fastapi import APIRouter, Depends

from app.dependencies import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
def list_jobs(current_user=Depends(get_current_user)) -> dict[str, list[dict[str, str]]]:
    return {"items": []}


@router.get("/{job_id}")
def get_job(job_id: str, current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"job_id": job_id, "status": "not-implemented"}

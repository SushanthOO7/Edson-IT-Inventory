from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.sync_run import SyncRun

settings = get_settings()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sync_intune_devices(db: Session, *, bearer_token: str, graph_url: str | None = None) -> SyncRun:
    if not bearer_token.strip():
        raise ValueError("bearer_token is required")

    run = SyncRun(
        source="INTUNE",
        started_at=_now_iso(),
        status="SUCCESS",
        total_records=0,
        matched_devices=0,
        created_devices=0,
        conflicts_created=0,
        errors_count=0,
        error_log={"graph_url": graph_url or settings.intune_graph_url, "note": "Intune sync scaffold is ready for Graph pagination"},
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

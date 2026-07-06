from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.data_conflict import DataConflict
from app.models.device import Device


def list_conflicts(db: Session) -> list[DataConflict]:
    return list(db.scalars(select(DataConflict).order_by(DataConflict.created_at.desc())))


def get_conflict(db: Session, conflict_id: str) -> DataConflict | None:
    return db.get(DataConflict, conflict_id)


def resolve_conflict(db: Session, conflict_id: str, *, resolved_value: str | None, resolved_by: str | None, status: str = "RESOLVED") -> DataConflict | None:
    conflict = get_conflict(db, conflict_id)
    if not conflict:
        return None
    conflict.resolved_value = resolved_value
    conflict.resolved_by = resolved_by
    conflict.status = status
    conflict.resolved_at = conflict.resolved_at or datetime.now(timezone.utc).isoformat()

    if status == "RESOLVED" and resolved_value is not None:
        device = db.get(Device, conflict.device_id)
        if device and hasattr(device, conflict.field_name):
            setattr(device, conflict.field_name, resolved_value)
            db.add(device)

    db.add(conflict)
    db.commit()
    db.refresh(conflict)
    return conflict

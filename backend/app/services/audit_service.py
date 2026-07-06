from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(db: Session, *, user_id: str | None, action: str, entity_type: str | None = None, entity_id: str | None = None, old_value: dict | None = None, new_value: dict | None = None, ip_address: str | None = None) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

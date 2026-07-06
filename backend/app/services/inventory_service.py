from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.inventory_event import InventoryEvent
from app.models.office_inventory import OfficeInventory


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_or_create_office_inventory(db: Session, device_id: str) -> OfficeInventory:
    office_inventory = db.scalar(select(OfficeInventory).where(OfficeInventory.device_id == device_id))
    if office_inventory:
        return office_inventory
    office_inventory = OfficeInventory(device_id=device_id, current_status="IN_OFFICE")
    db.add(office_inventory)
    db.commit()
    db.refresh(office_inventory)
    return office_inventory


def create_inventory_event(db: Session, device_id: str, event_type: str, from_status: str | None, to_status: str | None, performed_by: str | None = None, assigned_to_name: str | None = None, assigned_to_email: str | None = None, location: str | None = None, condition: str | None = None, notes: str | None = None) -> InventoryEvent:
    event = InventoryEvent(
        device_id=device_id,
        event_type=event_type,
        from_status=from_status,
        to_status=to_status,
        performed_by=performed_by,
        assigned_to_name=assigned_to_name,
        assigned_to_email=assigned_to_email,
        location=location,
        condition=condition,
        notes=notes,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def set_status(db: Session, device_id: str, status: str, *, performed_by: str | None = None, location: str | None = None, condition: str | None = None, notes: str | None = None, assigned_to_name: str | None = None, assigned_to_email: str | None = None, event_type: str = "UPDATED_MANUALLY") -> OfficeInventory:
    office_inventory = get_or_create_office_inventory(db, device_id)
    previous_status = office_inventory.current_status
    office_inventory.current_status = status
    office_inventory.current_location = location or office_inventory.current_location
    office_inventory.condition = condition or office_inventory.condition
    office_inventory.notes = notes or office_inventory.notes
    office_inventory.assigned_user_name = assigned_to_name or office_inventory.assigned_user_name
    office_inventory.assigned_user_email = assigned_to_email or office_inventory.assigned_user_email
    office_inventory.updated_at = datetime.now(timezone.utc)
    db.add(office_inventory)
    db.commit()
    db.refresh(office_inventory)
    create_inventory_event(
        db,
        device_id=device_id,
        event_type=event_type,
        from_status=previous_status,
        to_status=status,
        performed_by=performed_by,
        assigned_to_name=assigned_to_name,
        assigned_to_email=assigned_to_email,
        location=location,
        condition=condition,
        notes=notes,
    )
    return office_inventory


def add_to_office(db: Session, device_id: str, *, performed_by: str | None = None, location: str | None = None, condition: str | None = None, notes: str | None = None) -> OfficeInventory:
    return set_status(db, device_id, "IN_OFFICE", performed_by=performed_by, location=location, condition=condition, notes=notes, event_type="ADDED_TO_OFFICE")


def check_out(db: Session, device_id: str, *, checked_out_to: str | None = None, assigned_to_email: str | None = None, performed_by: str | None = None, expected_return_at: str | None = None, notes: str | None = None) -> OfficeInventory:
    office_inventory = get_or_create_office_inventory(db, device_id)
    previous_status = office_inventory.current_status
    office_inventory.current_status = "CHECKED_OUT"
    office_inventory.checked_out_to = checked_out_to or office_inventory.checked_out_to
    office_inventory.assigned_user_email = assigned_to_email or office_inventory.assigned_user_email
    office_inventory.checked_out_by = performed_by or office_inventory.checked_out_by
    office_inventory.checked_out_at = _now_iso()
    office_inventory.expected_return_at = expected_return_at or office_inventory.expected_return_at
    office_inventory.notes = notes or office_inventory.notes
    db.add(office_inventory)
    db.commit()
    db.refresh(office_inventory)
    create_inventory_event(db, device_id, "CHECKED_OUT", previous_status, "CHECKED_OUT", performed_by=performed_by, assigned_to_email=assigned_to_email, assigned_to_name=checked_out_to, notes=notes)
    return office_inventory


def check_in(db: Session, device_id: str, *, performed_by: str | None = None, condition: str | None = None, notes: str | None = None) -> OfficeInventory:
    return set_status(db, device_id, "IN_OFFICE", performed_by=performed_by, condition=condition, notes=notes, event_type="CHECKED_IN")


def move_to_storage(db: Session, device_id: str, *, performed_by: str | None = None, location: str | None = None, notes: str | None = None) -> OfficeInventory:
    return set_status(db, device_id, "STORED", performed_by=performed_by, location=location, notes=notes, event_type="MOVED_TO_STORAGE")


def mark_under_repair(db: Session, device_id: str, *, performed_by: str | None = None, notes: str | None = None, condition: str | None = "NEEDS_REPAIR") -> OfficeInventory:
    return set_status(db, device_id, "UNDER_REPAIR", performed_by=performed_by, condition=condition, notes=notes, event_type="MARKED_UNDER_REPAIR")


def mark_missing(db: Session, device_id: str, *, performed_by: str | None = None, notes: str | None = None) -> OfficeInventory:
    return set_status(db, device_id, "MISSING", performed_by=performed_by, notes=notes, event_type="MARKED_MISSING")


def mark_retired(db: Session, device_id: str, *, performed_by: str | None = None, notes: str | None = None) -> OfficeInventory:
    return set_status(db, device_id, "RETIRED", performed_by=performed_by, notes=notes, event_type="MARKED_RETIRED")


def mark_disposed(db: Session, device_id: str, *, performed_by: str | None = None, notes: str | None = None) -> OfficeInventory:
    return set_status(db, device_id, "DISPOSED", performed_by=performed_by, notes=notes, event_type="MARKED_DISPOSED")

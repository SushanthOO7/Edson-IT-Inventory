from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.office_inventory import OfficeInventory
from app.schemas.inventory import InventoryActionRequest, InventoryEventRead, OfficeInventoryRead
from app.services import inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/office", response_model=list[OfficeInventoryRead])
def list_office_inventory(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[OfficeInventory]:
    return list(db.scalars(select(OfficeInventory).order_by(OfficeInventory.updated_at.desc())))


@router.get("/checked-out", response_model=list[OfficeInventoryRead])
def list_checked_out(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[OfficeInventory]:
    return list(db.scalars(select(OfficeInventory).where(OfficeInventory.current_status == "CHECKED_OUT").order_by(OfficeInventory.updated_at.desc())))


@router.post("/add-to-office", response_model=OfficeInventoryRead)
def add_to_office(payload: InventoryActionRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> OfficeInventory:
    return inventory_service.add_to_office(db, payload.device_id, performed_by=current_user.email, location=payload.current_location, condition=payload.condition, notes=payload.notes)


@router.post("/check-out", response_model=OfficeInventoryRead)
def check_out(payload: InventoryActionRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> OfficeInventory:
    return inventory_service.check_out(db, payload.device_id, checked_out_to=payload.checked_out_to, assigned_to_email=payload.assigned_user_email, performed_by=current_user.email, expected_return_at=payload.expected_return_at, notes=payload.notes)


@router.post("/check-in", response_model=OfficeInventoryRead)
def check_in(payload: InventoryActionRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> OfficeInventory:
    return inventory_service.check_in(db, payload.device_id, performed_by=current_user.email, condition=payload.condition, notes=payload.notes)


@router.post("/mark-under-repair", response_model=OfficeInventoryRead)
def mark_under_repair(payload: InventoryActionRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> OfficeInventory:
    return inventory_service.mark_under_repair(db, payload.device_id, performed_by=current_user.email, notes=payload.notes, condition=payload.condition)


@router.post("/move-to-storage", response_model=OfficeInventoryRead)
def move_to_storage(payload: InventoryActionRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> OfficeInventory:
    return inventory_service.move_to_storage(db, payload.device_id, performed_by=current_user.email, location=payload.current_location, notes=payload.notes)


@router.post("/mark-missing", response_model=OfficeInventoryRead)
def mark_missing(payload: InventoryActionRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> OfficeInventory:
    return inventory_service.mark_missing(db, payload.device_id, performed_by=current_user.email, notes=payload.notes)


@router.post("/mark-retired", response_model=OfficeInventoryRead)
def mark_retired(payload: InventoryActionRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> OfficeInventory:
    return inventory_service.mark_retired(db, payload.device_id, performed_by=current_user.email, notes=payload.notes)


@router.post("/mark-disposed", response_model=OfficeInventoryRead)
def mark_disposed(payload: InventoryActionRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> OfficeInventory:
    return inventory_service.mark_disposed(db, payload.device_id, performed_by=current_user.email, notes=payload.notes)

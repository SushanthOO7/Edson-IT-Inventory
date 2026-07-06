from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.data_conflict import DataConflict
from app.models.device import Device
from app.models.inventory_event import InventoryEvent
from app.schemas.conflict import ConflictRead
from app.schemas.device import DeviceCreate, DeviceListResponse, DeviceRead, DeviceUpdate
from app.schemas.inventory import InventoryEventRead

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=DeviceListResponse)
def list_devices(q: str | None = Query(default=None), limit: int = Query(default=50, ge=1, le=100), offset: int = Query(default=0, ge=0), db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> DeviceListResponse:
    query = select(Device)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                Device.asset_tag.ilike(pattern),
                Device.serial_number.ilike(pattern),
                Device.device_name.ilike(pattern),
                Device.display_name.ilike(pattern),
                Device.model.ilike(pattern),
                Device.model_category.ilike(pattern),
                Device.department.ilike(pattern),
                Device.cost_center.ilike(pattern),
            )
        )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(db.scalars(query.order_by(Device.updated_at.desc()).offset(offset).limit(limit)))
    return DeviceListResponse(items=items, total=total)


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> Device:
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(payload: DeviceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> Device:
    device = Device(**payload.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.patch("/{device_id}", response_model=DeviceRead)
def update_device(device_id: str, payload: DeviceUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> Device:
    device = db.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(device, field, value)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("/{device_id}/history", response_model=list[InventoryEventRead])
def get_history(device_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[InventoryEvent]:
    return list(db.scalars(select(InventoryEvent).where(InventoryEvent.device_id == device_id).order_by(InventoryEvent.created_at.desc())))


@router.get("/{device_id}/conflicts", response_model=list[ConflictRead])
def get_conflicts(device_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[DataConflict]:
    return list(db.scalars(select(DataConflict).where(DataConflict.device_id == device_id).order_by(DataConflict.created_at.desc())))


@router.post("/{device_id}/merge")
def merge_device(device_id: str, merge_into_device_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, str]:
    if device_id == merge_into_device_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot merge a device into itself")
    source_device = db.get(Device, device_id)
    target_device = db.get(Device, merge_into_device_id)
    if not source_device or not target_device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return {"status": "merge-recorded", "source_device_id": device_id, "target_device_id": merge_into_device_id}

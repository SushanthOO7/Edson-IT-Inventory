from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.data_conflict import DataConflict
from app.models.device import Device
from app.models.inventory_event import InventoryEvent
from app.models.office_inventory import OfficeInventory
from app.models.service_now_asset import ServiceNowAsset


SEED_DEVICE_NOTES = "Seeded device for local development"
SEED_ASSET_TAGS = {"CON4136579", "CON4136580", "CON4136591"}


def seed_sample_data(db: Session) -> None:
    return None


def cleanup_seed_sample_data(db: Session) -> int:
    seed_devices = list(
        db.scalars(
            select(Device).where(
                (Device.notes == SEED_DEVICE_NOTES) | (Device.asset_tag.in_(SEED_ASSET_TAGS))
            )
        )
    )
    seed_device_ids = [device.id for device in seed_devices]
    if not seed_device_ids:
        return 0

    affected_assets = list(db.scalars(select(ServiceNowAsset).where(ServiceNowAsset.device_id.in_(seed_device_ids))))
    db.execute(delete(OfficeInventory).where(OfficeInventory.device_id.in_(seed_device_ids)))
    db.execute(delete(InventoryEvent).where(InventoryEvent.device_id.in_(seed_device_ids)))
    db.execute(delete(DataConflict).where(DataConflict.device_id.in_(seed_device_ids)))
    db.execute(delete(Device).where(Device.id.in_(seed_device_ids)))
    db.flush()

    for asset in affected_assets:
        device = None
        if asset.asset_tag:
            device = db.scalar(select(Device).where(Device.asset_tag == asset.asset_tag))
        if not device and asset.serial_number:
            device = db.scalar(select(Device).where(Device.serial_number == asset.serial_number))
        if not device:
            device = Device(
                asset_tag=asset.asset_tag,
                serial_number=asset.serial_number,
                device_name=asset.display_name or asset.asset_tag,
                display_name=asset.display_name,
                model=asset.model_category,
                model_category=asset.model_category,
                mac_address=asset.u_mac_address,
                department=asset.department,
                cost_center=asset.u_cost_center,
                lifecycle_status="PENDING_REVIEW",
                source_confidence=100.0,
                notes=asset.comments,
            )
            db.add(device)
            db.flush()
        asset.device_id = device.id
        db.add(asset)

    db.commit()
    return len(seed_device_ids)

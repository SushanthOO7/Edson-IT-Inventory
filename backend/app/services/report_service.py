from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.data_conflict import DataConflict
from app.models.device import Device
from app.models.import_run import ImportRun
from app.models.inventory_event import InventoryEvent
from app.models.office_inventory import OfficeInventory
from app.models.sync_run import SyncRun


def dashboard_summary(db: Session) -> dict[str, int | str | None]:
    total_devices = db.scalar(select(func.count()).select_from(Device)) or 0
    in_office = db.scalar(select(func.count()).select_from(OfficeInventory).where(OfficeInventory.current_status == "IN_OFFICE")) or 0
    checked_out = db.scalar(select(func.count()).select_from(OfficeInventory).where(OfficeInventory.current_status == "CHECKED_OUT")) or 0
    under_repair = db.scalar(select(func.count()).select_from(OfficeInventory).where(OfficeInventory.current_status == "UNDER_REPAIR")) or 0
    missing = db.scalar(select(func.count()).select_from(OfficeInventory).where(OfficeInventory.current_status == "MISSING")) or 0
    open_conflicts = db.scalar(select(func.count()).select_from(DataConflict).where(DataConflict.status == "OPEN")) or 0
    last_servicenow_import = db.scalar(select(ImportRun.finished_at).where(ImportRun.source == "EMAIL").order_by(ImportRun.finished_at.desc()))
    last_intune_sync = db.scalar(select(SyncRun.finished_at).order_by(SyncRun.finished_at.desc()))
    return {
        "total_devices": total_devices,
        "in_office": in_office,
        "checked_out": checked_out,
        "under_repair": under_repair,
        "missing": missing,
        "open_conflicts": open_conflicts,
        "last_servicenow_import": last_servicenow_import,
        "last_intune_sync": last_intune_sync,
    }

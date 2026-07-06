import csv
from datetime import datetime, timezone
from io import StringIO

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.data_conflict import DataConflict
from app.models.device import Device
from app.models.import_run import ImportRun
from app.models.intune_device import IntuneDevice
from app.models.inventory_event import InventoryEvent
from app.models.office_inventory import OfficeInventory
from app.models.service_now_asset import ServiceNowAsset
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


def _device_map(db: Session) -> dict[str, Device]:
    return {device.id: device for device in db.scalars(select(Device))}


def _inventory_rows(db: Session, statuses: set[str] | None = None) -> list[dict[str, str | float | None]]:
    devices = _device_map(db)
    query = select(OfficeInventory).order_by(OfficeInventory.updated_at.desc())
    if statuses:
        query = query.where(OfficeInventory.current_status.in_(statuses))

    rows: list[dict[str, str | float | None]] = []
    for row in db.scalars(query):
        device = devices.get(row.device_id)
        rows.append(
            {
                "device_id": row.device_id,
                "asset_tag": device.asset_tag if device else None,
                "serial_number": device.serial_number if device else None,
                "display_name": (device.display_name or device.device_name) if device else None,
                "model": (device.model or device.model_category) if device else None,
                "department": device.department if device else None,
                "source_confidence": device.source_confidence if device else None,
                "current_status": row.current_status,
                "current_location": row.current_location,
                "assigned_user_name": row.assigned_user_name or row.checked_out_to,
                "assigned_user_email": row.assigned_user_email,
                "checked_out_by": row.checked_out_by,
                "checked_out_at": row.checked_out_at,
                "expected_return_at": row.expected_return_at,
                "condition": row.condition,
                "notes": row.notes,
            }
        )
    return rows


def office_inventory_report(db: Session) -> list[dict[str, str | float | None]]:
    return _inventory_rows(db)


def checked_out_report(db: Session) -> list[dict[str, str | float | None]]:
    return _inventory_rows(db, {"CHECKED_OUT"})


def overdue_report(db: Session) -> list[dict[str, str | float | None]]:
    now = datetime.now(timezone.utc)
    rows: list[dict[str, str | float | None]] = []
    for row in _inventory_rows(db, {"CHECKED_OUT"}):
        expected_return_at = row.get("expected_return_at")
        if not expected_return_at:
            continue
        try:
            expected = datetime.fromisoformat(str(expected_return_at).replace("Z", "+00:00"))
        except ValueError:
            rows.append(row)
            continue
        if expected < now:
            rows.append(row)
    return rows


def missing_report(db: Session) -> list[dict[str, str | float | None]]:
    return _inventory_rows(db, {"MISSING"})


def servicenow_not_intune_report(db: Session) -> list[dict[str, str | None]]:
    intune_device_ids = {device_id for device_id in db.scalars(select(IntuneDevice.device_id)) if device_id}
    rows: list[dict[str, str | None]] = []
    for asset in db.scalars(select(ServiceNowAsset).order_by(ServiceNowAsset.updated_at.desc())):
        if asset.device_id and asset.device_id in intune_device_ids:
            continue
        rows.append(
            {
                "device_id": asset.device_id,
                "asset_tag": asset.asset_tag,
                "serial_number": asset.serial_number,
                "display_name": asset.display_name,
                "assigned_to": asset.assigned_to or asset.u_assigned_to,
                "department": asset.department,
                "install_status": asset.install_status,
                "imported_at": asset.imported_at,
            }
        )
    return rows


def intune_not_servicenow_report(db: Session) -> list[dict[str, str | None]]:
    servicenow_device_ids = {device_id for device_id in db.scalars(select(ServiceNowAsset.device_id)) if device_id}
    rows: list[dict[str, str | None]] = []
    for device in db.scalars(select(IntuneDevice).order_by(IntuneDevice.updated_at.desc())):
        if device.device_id and device.device_id in servicenow_device_ids:
            continue
        rows.append(
            {
                "device_id": device.device_id,
                "intune_id": device.intune_id,
                "device_name": device.device_name,
                "user_principal_name": device.user_principal_name,
                "compliance_state": device.compliance_state,
                "management_state": device.management_state,
                "last_sync_datetime": device.last_sync_datetime,
                "synced_at": device.synced_at,
            }
        )
    return rows


def conflicts_report(db: Session) -> list[dict[str, str | None]]:
    rows: list[dict[str, str | None]] = []
    for conflict in db.scalars(select(DataConflict).where(DataConflict.status == "OPEN").order_by(DataConflict.created_at.desc())):
        rows.append(
            {
                "id": conflict.id,
                "device_id": conflict.device_id,
                "field_name": conflict.field_name,
                "service_now_value": conflict.service_now_value,
                "intune_value": conflict.intune_value,
                "local_value": conflict.local_value,
                "ocr_value": conflict.ocr_value,
                "conflict_type": conflict.conflict_type,
                "severity": conflict.severity,
                "status": conflict.status,
                "resolved_value": conflict.resolved_value,
                "resolved_by": conflict.resolved_by,
                "resolved_at": conflict.resolved_at,
            }
        )
    return rows


def inventory_events_report(db: Session) -> list[dict[str, str | None]]:
    rows: list[dict[str, str | None]] = []
    for event in db.scalars(select(InventoryEvent).order_by(InventoryEvent.created_at.desc())):
        rows.append(
            {
                "id": event.id,
                "device_id": event.device_id,
                "event_type": event.event_type,
                "from_status": event.from_status,
                "to_status": event.to_status,
                "performed_by": event.performed_by,
                "assigned_to_name": event.assigned_to_name,
                "assigned_to_email": event.assigned_to_email,
                "location": event.location,
                "condition": event.condition,
                "notes": event.notes,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }
        )
    return rows


def devices_csv_export(db: Session) -> str:
    rows = _inventory_rows(db)
    inventory_by_device_id = {str(row["device_id"]): row for row in rows}
    output = StringIO()
    fieldnames = [
        "device_id",
        "asset_tag",
        "serial_number",
        "display_name",
        "model",
        "department",
        "lifecycle_status",
        "source_confidence",
        "current_status",
        "current_location",
        "assigned_user_name",
        "assigned_user_email",
        "expected_return_at",
        "condition",
        "notes",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for device in db.scalars(select(Device).order_by(Device.updated_at.desc())):
        inventory_row = inventory_by_device_id.get(device.id, {})
        writer.writerow(
            {
                "device_id": device.id,
                "asset_tag": device.asset_tag,
                "serial_number": device.serial_number,
                "display_name": device.display_name or device.device_name,
                "model": device.model or device.model_category,
                "department": device.department,
                "lifecycle_status": device.lifecycle_status,
                "source_confidence": device.source_confidence,
                "current_status": inventory_row.get("current_status"),
                "current_location": inventory_row.get("current_location"),
                "assigned_user_name": inventory_row.get("assigned_user_name"),
                "assigned_user_email": inventory_row.get("assigned_user_email"),
                "expected_return_at": inventory_row.get("expected_return_at"),
                "condition": inventory_row.get("condition"),
                "notes": inventory_row.get("notes") or device.notes,
            }
        )
    return output.getvalue()

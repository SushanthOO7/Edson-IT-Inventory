from datetime import datetime, timezone
from io import StringIO

import pandas as pd
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.data_conflict import DataConflict
from app.models.device import Device
from app.models.import_run import ImportRun
from app.models.service_now_asset import ServiceNowAsset
from app.utils.csv_validation import validate_required_columns

settings = get_settings()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _find_device_by_exact_identifiers(
    db: Session,
    *,
    asset_tag: str | None,
    serial_number: str | None,
    mac_address: str | None,
    ci: str | None,
) -> Device | None:
    conditions = []
    if asset_tag:
        conditions.append(Device.asset_tag == asset_tag)
    if serial_number:
        conditions.append(Device.serial_number == serial_number)
    if mac_address:
        conditions.append(Device.mac_address == mac_address)
    if ci:
        conditions.append(Device.device_name == ci)
    if not conditions:
        return None
    return db.scalar(select(Device).where(or_(*conditions)).limit(1))


def _sync_device_from_servicenow_row(
    device: Device,
    *,
    asset_tag: str | None,
    serial_number: str | None,
    device_name: str | None,
    model_category: str | None,
    department: str | None,
    mac_address: str | None,
    cost_center: str | None,
    comments: str | None,
) -> None:
    device.asset_tag = asset_tag or device.asset_tag
    device.serial_number = serial_number or device.serial_number
    device.device_name = device.device_name or device_name or asset_tag
    device.display_name = device_name or device.display_name
    device.model = model_category or device.model
    device.model_category = model_category or device.model_category
    device.mac_address = mac_address or device.mac_address
    device.department = department or device.department
    device.cost_center = cost_center or device.cost_center
    device.notes = comments or device.notes
    if device.lifecycle_status == "UNKNOWN":
        device.lifecycle_status = "PENDING_REVIEW"
    device.source_confidence = max(device.source_confidence or 0.0, 100.0)


def import_servicenow_csv(db: Session, csv_text: str, *, source: str = "MANUAL_UPLOAD", file_name: str | None = None, email_subject: str | None = None, email_received_at: str | None = None) -> ImportRun:
    required_columns = [column.strip() for column in settings.servicenow_required_columns.split(",") if column.strip()]
    missing = validate_required_columns(csv_text, required_columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    dataframe = pd.read_csv(StringIO(csv_text)).fillna("")
    db.execute(delete(DataConflict).where(DataConflict.conflict_type == "LOW_CONFIDENCE_MATCH", DataConflict.field_name == "match_confidence"))
    db.commit()

    run = ImportRun(
        source=source,
        started_at=_now_iso(),
        status="RUNNING",
        file_name=file_name,
        email_subject=email_subject,
        email_received_at=email_received_at,
        total_rows=len(dataframe.index),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    created_devices = 0
    updated_devices = 0
    matched_devices = 0
    conflicts_created = 0

    for row in dataframe.to_dict(orient="records"):
        serial_number = str(row.get("serial_number", "")).strip() or None
        asset_tag = str(row.get("asset_tag", "")).strip() or None
        device_name = str(row.get("display_name", "")).strip() or None
        model_category = str(row.get("model_category", "")).strip() or None
        department = str(row.get("department", "")).strip() or None
        mac_address = str(row.get("u_mac_address", "")).strip() or None
        ci = str(row.get("ci", "")).strip() or None
        cost_center = str(row.get("u_cost_center", "")).strip() or None
        comments = str(row.get("comments", "")).strip() or None

        service_now_asset = db.scalar(select(ServiceNowAsset).where(ServiceNowAsset.asset_tag == asset_tag)) if asset_tag else None
        device = db.get(Device, service_now_asset.device_id) if service_now_asset and service_now_asset.device_id else None
        if not device:
            device = _find_device_by_exact_identifiers(
                db,
                asset_tag=asset_tag,
                serial_number=serial_number,
                mac_address=mac_address,
                ci=ci,
            )

        if device:
            matched_devices += 1
            _sync_device_from_servicenow_row(
                device,
                asset_tag=asset_tag,
                serial_number=serial_number,
                device_name=device_name,
                model_category=model_category,
                department=department,
                mac_address=mac_address,
                cost_center=cost_center,
                comments=comments,
            )
            db.add(device)
        else:
            device = Device(
                asset_tag=asset_tag,
                serial_number=serial_number,
                device_name=device_name,
                display_name=device_name,
                model_category=model_category,
                department=department,
                mac_address=mac_address,
                cost_center=cost_center,
                lifecycle_status="PENDING_REVIEW",
                source_confidence=100.0,
                notes=comments,
            )
            db.add(device)
            db.commit()
            db.refresh(device)
            created_devices += 1

        if service_now_asset:
            service_now_asset.device_id = device.id
            service_now_asset.model_category = model_category
            service_now_asset.display_name = device_name
            service_now_asset.u_assigned_to = str(row.get("u_assigned_to", "")).strip() or None
            service_now_asset.assigned_to = str(row.get("assigned_to", "")).strip() or None
            service_now_asset.u_cost_center = cost_center
            service_now_asset.install_status = str(row.get("install_status", "")).strip() or None
            service_now_asset.serial_number = serial_number
            service_now_asset.u_mac_address = mac_address
            service_now_asset.ci = ci
            service_now_asset.comments = comments
            service_now_asset.department = department
            service_now_asset.import_run_id = run.id
            service_now_asset.imported_at = _now_iso()
            service_now_asset.raw_json = row
            updated_devices += 1
        else:
            service_now_asset = ServiceNowAsset(
                device_id=device.id,
                asset_tag=asset_tag,
                model_category=model_category,
                display_name=device_name,
                u_assigned_to=str(row.get("u_assigned_to", "")).strip() or None,
                assigned_to=str(row.get("assigned_to", "")).strip() or None,
                u_cost_center=cost_center,
                install_status=str(row.get("install_status", "")).strip() or None,
                serial_number=serial_number,
                u_mac_address=mac_address,
                ci=ci,
                comments=comments,
                department=department,
                imported_at=_now_iso(),
                import_run_id=run.id,
                raw_json=row,
            )
            db.add(service_now_asset)
            updated_devices += 1

        db.commit()

    run.status = "SUCCESS"
    run.finished_at = _now_iso()
    run.created_devices = created_devices
    run.updated_devices = updated_devices
    run.matched_devices = matched_devices
    run.conflicts_created = conflicts_created
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

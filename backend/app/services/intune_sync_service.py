from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.data_conflict import DataConflict
from app.models.device import Device
from app.models.intune_device import IntuneDevice
from app.models.sync_run import SyncRun
from app.services.device_matching_service import match_device

settings = get_settings()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _bool_or_none(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def _normalize_token(token: str) -> str:
    token = token.strip()
    if not token:
        raise ValueError("bearer_token is required")
    return token.removeprefix("Bearer ").removeprefix("bearer ").strip()


def _fetch_managed_devices(*, bearer_token: str, graph_url: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    next_url: str | None = graph_url
    params: dict[str, int] | None = {"$top": settings.intune_page_size}
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Accept": "application/json",
    }

    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        while next_url:
            response = client.get(next_url, headers=headers, params=params)
            params = None
            if response.status_code >= 400:
                detail = response.text[:500]
                raise ValueError(f"Microsoft Graph request failed ({response.status_code}): {detail}")

            payload = response.json()
            page = payload.get("value")
            if not isinstance(page, list):
                raise ValueError("Microsoft Graph response did not contain a device value list")

            records.extend(record for record in page if isinstance(record, dict))
            next_link = payload.get("@odata.nextLink")
            next_url = str(next_link) if next_link else None

    return records


def _existing_intune_device(db: Session, intune_id: str | None) -> IntuneDevice | None:
    if not intune_id:
        return None
    return db.scalar(select(IntuneDevice).where(IntuneDevice.intune_id == intune_id))


def _sync_device_fields(device: Device, record: dict[str, Any]) -> None:
    device_name = _string(record.get("deviceName"))
    serial_number = _string(record.get("serialNumber"))
    device_type = _string(record.get("deviceType") or record.get("operatingSystem"))

    device.serial_number = device.serial_number or serial_number
    device.device_name = device.device_name or device_name
    device.display_name = device.display_name or device_name
    device.device_type = device.device_type or device_type
    if device.lifecycle_status == "UNKNOWN":
        device.lifecycle_status = "PENDING_REVIEW"
    device.source_confidence = max(device.source_confidence or 0.0, 70.0)


def _open_conflict_exists(db: Session, *, device_id: str, field_name: str) -> bool:
    return bool(
        db.scalar(
            select(DataConflict.id)
            .where(
                DataConflict.device_id == device_id,
                DataConflict.field_name == field_name,
                DataConflict.conflict_type == "INTUNE_MISMATCH",
                DataConflict.status == "OPEN",
            )
            .limit(1)
        )
    )


def _record_conflict(db: Session, *, device: Device, field_name: str, local_value: str | None, intune_value: str | None) -> bool:
    if not local_value or not intune_value or local_value.strip().lower() == intune_value.strip().lower():
        return False
    if _open_conflict_exists(db, device_id=device.id, field_name=field_name):
        return False

    db.add(
        DataConflict(
            device_id=device.id,
            field_name=field_name,
            local_value=local_value,
            intune_value=intune_value,
            conflict_type="INTUNE_MISMATCH",
            severity="MEDIUM",
            status="OPEN",
        )
    )
    return True


def _upsert_intune_snapshot(db: Session, *, record: dict[str, Any], run: SyncRun, device: Device | None) -> IntuneDevice:
    intune_id = _string(record.get("id"))
    snapshot = _existing_intune_device(db, intune_id)
    if not snapshot:
        snapshot = IntuneDevice(intune_id=intune_id)

    snapshot.device_id = device.id if device else None
    snapshot.device_name = _string(record.get("deviceName"))
    snapshot.management_agent = _string(record.get("managementAgent"))
    snapshot.owner_type = _string(record.get("ownerType"))
    snapshot.compliance_state = _string(record.get("complianceState"))
    snapshot.device_type = _string(record.get("deviceType") or record.get("operatingSystem"))
    snapshot.os_version = _string(record.get("osVersion"))
    snapshot.user_principal_name = _string(record.get("userPrincipalName") or record.get("emailAddress"))
    snapshot.last_sync_datetime = _string(record.get("lastSyncDateTime"))
    snapshot.device_registration_state = _string(record.get("deviceRegistrationState"))
    snapshot.management_state = _string(record.get("managementState"))
    snapshot.exchange_access_state = _string(record.get("exchangeAccessState"))
    snapshot.exchange_access_state_reason = _string(record.get("exchangeAccessStateReason"))
    snapshot.jail_broken = _bool_or_none(record.get("jailBroken"))
    snapshot.enrolled_datetime = _string(record.get("enrolledDateTime"))
    snapshot.device_enrollment_type = _string(record.get("deviceEnrollmentType"))
    snapshot.synced_at = _now_iso()
    snapshot.sync_run_id = run.id
    snapshot.raw_json = record
    db.add(snapshot)
    return snapshot


def sync_intune_devices(db: Session, *, bearer_token: str, graph_url: str | None = None) -> SyncRun:
    normalized_token = _normalize_token(bearer_token)
    url = (graph_url or settings.intune_graph_url).strip()
    run = SyncRun(source="INTUNE", started_at=_now_iso(), status="RUNNING", error_log={"graph_url": url})
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        records = _fetch_managed_devices(bearer_token=normalized_token, graph_url=url)
    except ValueError as exc:
        run.status = "FAILED"
        run.finished_at = _now_iso()
        run.errors_count = 1
        run.error_log = {"graph_url": url, "error": str(exc)}
        db.add(run)
        db.commit()
        db.refresh(run)
        raise

    matched_devices = 0
    created_devices = 0
    conflicts_created = 0

    for record in records:
        intune_id = _string(record.get("id"))
        device_name = _string(record.get("deviceName"))
        serial_number = _string(record.get("serialNumber"))
        user_principal_name = _string(record.get("userPrincipalName") or record.get("emailAddress"))

        existing_snapshot = _existing_intune_device(db, intune_id)
        device = db.get(Device, existing_snapshot.device_id) if existing_snapshot and existing_snapshot.device_id else None
        if not device:
            candidate = match_device(
                db,
                serial_number=serial_number,
                device_name=device_name,
                display_name=device_name,
                assigned_user=user_principal_name,
                intune_id=intune_id,
            )
            device = candidate.device if candidate else None

        if device:
            matched_devices += 1
            conflicts_created += int(
                _record_conflict(
                    db,
                    device=device,
                    field_name="device_name",
                    local_value=device.device_name,
                    intune_value=device_name,
                )
            )
            _sync_device_fields(device, record)
            db.add(device)
        else:
            device = Device(
                serial_number=serial_number,
                device_name=device_name,
                display_name=device_name,
                device_type=_string(record.get("deviceType") or record.get("operatingSystem")),
                lifecycle_status="PENDING_REVIEW",
                source_confidence=70.0,
                notes="Created from Intune sync",
            )
            db.add(device)
            db.commit()
            db.refresh(device)
            created_devices += 1

        _upsert_intune_snapshot(db, record=record, run=run, device=device)
        db.commit()

    run.status = "SUCCESS"
    run.finished_at = _now_iso()
    run.total_records = len(records)
    run.matched_devices = matched_devices
    run.created_devices = created_devices
    run.conflicts_created = conflicts_created
    run.errors_count = 0
    run.error_log = {"graph_url": url}
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

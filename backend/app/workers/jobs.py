from app.database import SessionLocal
from app.services.intune_sync_service import sync_intune_devices
from app.services.servicenow_import_service import import_servicenow_csv


def run_servicenow_import(csv_text: str) -> dict[str, str | int]:
    db = SessionLocal()
    try:
        run = import_servicenow_csv(db, csv_text, source="BACKGROUND_JOB")
        return {
            "status": run.status,
            "job": "servicenow-import",
            "run_id": run.id,
            "total_rows": run.total_rows,
            "created_devices": run.created_devices,
            "matched_devices": run.matched_devices,
            "conflicts_created": run.conflicts_created,
        }
    finally:
        db.close()


def run_intune_sync(bearer_token: str, graph_url: str | None = None) -> dict[str, str | int]:
    db = SessionLocal()
    try:
        run = sync_intune_devices(db, bearer_token=bearer_token, graph_url=graph_url)
        return {
            "status": run.status,
            "job": "intune-sync",
            "run_id": run.id,
            "total_records": run.total_records,
            "created_devices": run.created_devices,
            "matched_devices": run.matched_devices,
            "conflicts_created": run.conflicts_created,
        }
    finally:
        db.close()

from app.services.intune_sync_service import sync_intune_devices
from app.services.servicenow_import_service import import_servicenow_csv


def run_servicenow_import(csv_text: str) -> dict[str, str]:
    return {"status": "queued", "job": "servicenow-import", "csv_length": str(len(csv_text))}


def run_intune_sync(bearer_token: str, graph_url: str | None = None) -> dict[str, str | None]:
    return {"status": "queued", "job": "intune-sync", "graph_url": graph_url}

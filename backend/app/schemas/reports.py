from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_devices: int
    in_office: int
    checked_out: int
    under_repair: int
    missing: int
    open_conflicts: int
    last_servicenow_import: str | None = None
    last_intune_sync: str | None = None

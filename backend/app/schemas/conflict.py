from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConflictResolveRequest(BaseModel):
    resolved_value: str | None = None
    status: str = "RESOLVED"


class ConflictRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str
    field_name: str
    service_now_value: str | None
    intune_value: str | None
    local_value: str | None
    ocr_value: str | None
    conflict_type: str | None
    severity: str
    status: str
    resolved_value: str | None
    resolved_by: str | None
    resolved_at: str | None
    created_at: datetime

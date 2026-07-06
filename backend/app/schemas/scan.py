from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScanConfirmRequest(BaseModel):
    scan_id: str
    device_id: str
    confirmed_by: str | None = None


class ScanResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str | None
    detected_asset_tag: str | None
    detected_serial_number: str | None
    detected_model: str | None
    detected_device_name: str | None
    detected_text: str | None
    confidence_score: float
    image_path: str | None
    scan_status: str
    confirmed_by: str | None
    confirmed_at: str | None
    created_at: datetime

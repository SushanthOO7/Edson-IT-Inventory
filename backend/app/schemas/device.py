from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DeviceBase(BaseModel):
    asset_tag: str | None = None
    serial_number: str | None = None
    device_name: str | None = None
    display_name: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    model_category: str | None = None
    device_type: str | None = None
    mac_address: str | None = None
    department: str | None = None
    cost_center: str | None = None
    lifecycle_status: str = "UNKNOWN"
    source_confidence: float = 0.0
    notes: str | None = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(DeviceBase):
    pass


class DeviceRead(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class DeviceListResponse(BaseModel):
    items: list[DeviceRead]
    total: int

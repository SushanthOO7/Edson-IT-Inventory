from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ServiceNowImportResponse(BaseModel):
    run_id: str
    status: str
    total_rows: int
    created_devices: int
    updated_devices: int
    matched_devices: int
    conflicts_created: int


class ImportRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source: str
    started_at: str | None
    finished_at: str | None
    status: str
    file_name: str | None
    email_subject: str | None
    email_received_at: str | None
    total_rows: int
    created_devices: int
    updated_devices: int
    matched_devices: int
    conflicts_created: int
    errors_count: int
    created_at: datetime


class ServiceNowAssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str | None
    asset_tag: str | None
    model_category: str | None
    display_name: str | None
    u_assigned_to: str | None
    assigned_to: str | None
    u_cost_center: str | None
    install_status: str | None
    serial_number: str | None
    u_mac_address: str | None
    ci: str | None
    comments: str | None
    department: str | None
    imported_at: str | None
    import_run_id: str | None
    raw_json: dict[str, Any] | None
    updated_at: datetime


class ServiceNowAssetFilters(BaseModel):
    departments: list[str]
    install_statuses: list[str]
    model_categories: list[str]
    assigned_to: list[str]


class ServiceNowAssetListResponse(BaseModel):
    items: list[ServiceNowAssetRead]
    total: int
    limit: int
    offset: int
    columns: list[str]
    filters: ServiceNowAssetFilters

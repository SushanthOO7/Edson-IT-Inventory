from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class InventoryActionRequest(BaseModel):
    device_id: str
    current_location: str | None = None
    assigned_user_name: str | None = None
    assigned_user_email: EmailStr | None = None
    checked_out_to: str | None = None
    checked_out_by: str | None = None
    expected_return_at: str | None = None
    checked_in_by: str | None = None
    condition: str | None = None
    notes: str | None = None


class OfficeInventoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str
    current_status: str
    current_location: str | None
    assigned_user_name: str | None
    assigned_user_email: EmailStr | None
    checked_out_to: str | None
    checked_out_by: str | None
    checked_out_at: str | None
    expected_return_at: str | None
    checked_in_by: str | None
    checked_in_at: str | None
    condition: str | None
    notes: str | None


class InventoryEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str
    event_type: str
    from_status: str | None
    to_status: str | None
    performed_by: str | None
    assigned_to_name: str | None
    assigned_to_email: str | None
    location: str | None
    condition: str | None
    notes: str | None
    created_at: datetime

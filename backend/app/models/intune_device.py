from sqlalchemy import Boolean, DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class IntuneDevice(IdMixin, TimestampMixin, Base):
    __tablename__ = "intune_devices"

    device_id: Mapped[str | None] = mapped_column(String(36), index=True)
    intune_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    device_name: Mapped[str | None] = mapped_column(String(255), index=True)
    management_agent: Mapped[str | None] = mapped_column(String(255))
    owner_type: Mapped[str | None] = mapped_column(String(255))
    compliance_state: Mapped[str | None] = mapped_column(String(255), index=True)
    device_type: Mapped[str | None] = mapped_column(String(255))
    os_version: Mapped[str | None] = mapped_column(String(255))
    user_principal_name: Mapped[str | None] = mapped_column(String(255), index=True)
    last_sync_datetime: Mapped[str | None] = mapped_column(String(50))
    device_registration_state: Mapped[str | None] = mapped_column(String(255))
    management_state: Mapped[str | None] = mapped_column(String(255))
    exchange_access_state: Mapped[str | None] = mapped_column(String(255))
    exchange_access_state_reason: Mapped[str | None] = mapped_column(String(255))
    jail_broken: Mapped[bool | None] = mapped_column(Boolean)
    enrolled_datetime: Mapped[str | None] = mapped_column(String(50))
    device_enrollment_type: Mapped[str | None] = mapped_column(String(255))
    synced_at: Mapped[str | None] = mapped_column(String(50))
    sync_run_id: Mapped[str | None] = mapped_column(String(36), index=True)
    raw_json: Mapped[dict | None] = mapped_column(JSON)

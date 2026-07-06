from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class DataConflict(IdMixin, TimestampMixin, Base):
    __tablename__ = "data_conflicts"

    device_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    field_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    service_now_value: Mapped[str | None] = mapped_column(Text())
    intune_value: Mapped[str | None] = mapped_column(Text())
    local_value: Mapped[str | None] = mapped_column(Text())
    ocr_value: Mapped[str | None] = mapped_column(Text())
    conflict_type: Mapped[str | None] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="MEDIUM")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN")
    resolved_value: Mapped[str | None] = mapped_column(Text())
    resolved_by: Mapped[str | None] = mapped_column(String(255))
    resolved_at: Mapped[str | None] = mapped_column(String(50))

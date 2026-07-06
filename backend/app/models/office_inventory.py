from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class OfficeInventory(IdMixin, TimestampMixin, Base):
    __tablename__ = "office_inventory"

    device_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    current_status: Mapped[str] = mapped_column(String(50), nullable=False, default="IN_OFFICE")
    current_location: Mapped[str | None] = mapped_column(String(255))
    assigned_user_name: Mapped[str | None] = mapped_column(String(255))
    assigned_user_email: Mapped[str | None] = mapped_column(String(255), index=True)
    checked_out_to: Mapped[str | None] = mapped_column(String(255))
    checked_out_by: Mapped[str | None] = mapped_column(String(255))
    checked_out_at: Mapped[str | None] = mapped_column(String(50))
    expected_return_at: Mapped[str | None] = mapped_column(String(50))
    checked_in_by: Mapped[str | None] = mapped_column(String(255))
    checked_in_at: Mapped[str | None] = mapped_column(String(50))
    condition: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text())

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class InventoryEvent(IdMixin, TimestampMixin, Base):
    __tablename__ = "inventory_events"

    device_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(50))
    to_status: Mapped[str | None] = mapped_column(String(50))
    performed_by: Mapped[str | None] = mapped_column(String(255))
    assigned_to_name: Mapped[str | None] = mapped_column(String(255))
    assigned_to_email: Mapped[str | None] = mapped_column(String(255), index=True)
    location: Mapped[str | None] = mapped_column(String(255))
    condition: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text())

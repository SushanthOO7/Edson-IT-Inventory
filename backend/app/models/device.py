from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class Device(IdMixin, TimestampMixin, Base):
    __tablename__ = "devices"

    asset_tag: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String(150), index=True)
    device_name: Mapped[str | None] = mapped_column(String(255), index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), index=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    model: Mapped[str | None] = mapped_column(String(255))
    model_category: Mapped[str | None] = mapped_column(String(255))
    device_type: Mapped[str | None] = mapped_column(String(255))
    mac_address: Mapped[str | None] = mapped_column(String(100), index=True)
    department: Mapped[str | None] = mapped_column(String(255), index=True)
    cost_center: Mapped[str | None] = mapped_column(String(255))
    lifecycle_status: Mapped[str] = mapped_column(String(50), nullable=False, default="UNKNOWN")
    source_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    notes: Mapped[str | None] = mapped_column(Text())

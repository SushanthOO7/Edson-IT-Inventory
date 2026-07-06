from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class ScanResult(IdMixin, TimestampMixin, Base):
    __tablename__ = "scan_results"

    device_id: Mapped[str | None] = mapped_column(String(36), index=True)
    detected_asset_tag: Mapped[str | None] = mapped_column(String(100), index=True)
    detected_serial_number: Mapped[str | None] = mapped_column(String(150), index=True)
    detected_model: Mapped[str | None] = mapped_column(String(255))
    detected_device_name: Mapped[str | None] = mapped_column(String(255))
    detected_text: Mapped[str | None] = mapped_column(Text())
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    image_path: Mapped[str | None] = mapped_column(String(500))
    scan_status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING_CONFIRMATION")
    confirmed_by: Mapped[str | None] = mapped_column(String(255))
    confirmed_at: Mapped[str | None] = mapped_column(String(50))

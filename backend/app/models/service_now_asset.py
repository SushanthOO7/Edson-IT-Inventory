from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class ServiceNowAsset(IdMixin, TimestampMixin, Base):
    __tablename__ = "service_now_assets"

    device_id: Mapped[str | None] = mapped_column(String(36), index=True)
    asset_tag: Mapped[str | None] = mapped_column(String(100), index=True)
    model_category: Mapped[str | None] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255))
    u_assigned_to: Mapped[str | None] = mapped_column(String(255))
    assigned_to: Mapped[str | None] = mapped_column(String(255), index=True)
    u_cost_center: Mapped[str | None] = mapped_column(String(255))
    install_status: Mapped[str | None] = mapped_column(String(255))
    serial_number: Mapped[str | None] = mapped_column(String(150), index=True)
    u_mac_address: Mapped[str | None] = mapped_column(String(100), index=True)
    ci: Mapped[str | None] = mapped_column(String(255), index=True)
    comments: Mapped[str | None] = mapped_column(Text())
    department: Mapped[str | None] = mapped_column(String(255), index=True)
    imported_at: Mapped[str | None] = mapped_column(String(50))
    import_run_id: Mapped[str | None] = mapped_column(String(36), index=True)
    raw_json: Mapped[dict | None] = mapped_column(JSON)

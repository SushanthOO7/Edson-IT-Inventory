from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class ImportRun(IdMixin, TimestampMixin, Base):
    __tablename__ = "import_runs"

    source: Mapped[str] = mapped_column(String(50), nullable=False, default="EMAIL")
    started_at: Mapped[str | None] = mapped_column(String(50))
    finished_at: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    file_name: Mapped[str | None] = mapped_column(String(255))
    email_subject: Mapped[str | None] = mapped_column(String(500))
    email_received_at: Mapped[str | None] = mapped_column(String(50))
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_devices: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_devices: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    matched_devices: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    conflicts_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errors_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_log: Mapped[dict | None] = mapped_column(JSON)

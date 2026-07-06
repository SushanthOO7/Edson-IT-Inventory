from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin, TimestampMixin


class EmailImportState(IdMixin, TimestampMixin, Base):
    __tablename__ = "email_import_state"

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    mailbox: Mapped[str] = mapped_column(String(255), nullable=False)
    last_processed_message_id: Mapped[str | None] = mapped_column(String(255))
    last_processed_received_at: Mapped[str | None] = mapped_column(String(50))
    last_successful_import_at: Mapped[str | None] = mapped_column(String(50))

from dataclasses import dataclass
from datetime import datetime, timezone
from email import policy
from email.message import EmailMessage, Message
from email.parser import BytesParser
import imaplib
import logging
import ssl

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.email_import_state import EmailImportState
from app.models.import_run import ImportRun
from app.services.servicenow_import_service import import_servicenow_csv

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailCsvAttachment:
    csv_text: str
    file_name: str
    message_id: str
    subject: str | None
    received_at: str | None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_app_password(password: str) -> str:
    return "".join(password.split())


def _ssl_context() -> ssl.SSLContext:
    settings = get_settings()
    if settings.email_tls_verify:
        return ssl.create_default_context()
    return ssl._create_unverified_context()


def _decode_bytes(payload: bytes, charset: str | None = None) -> str:
    encodings = [charset, "utf-8-sig", "utf-8", "latin-1"]
    for encoding in [item for item in encodings if item]:
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            continue
    return payload.decode("utf-8", errors="replace")


def _is_csv_part(part: Message) -> bool:
    file_name = part.get_filename() or ""
    content_type = part.get_content_type().lower()
    return file_name.lower().endswith(".csv") or content_type in {
        "text/csv",
        "application/csv",
        "application/vnd.ms-excel",
    }


def _extract_csv_attachment(message: EmailMessage, message_id: str) -> tuple[str, str] | None:
    for part in message.walk():
        if part.is_multipart() or not _is_csv_part(part):
            continue

        payload = part.get_payload(decode=True)
        if payload is None:
            content = part.get_content()
            if isinstance(content, str):
                return part.get_filename() or "servicenow-email.csv", content
            continue

        return part.get_filename() or f"servicenow-{message_id}.csv", _decode_bytes(payload, part.get_content_charset())

    return None


def _passes_filters(message: EmailMessage) -> bool:
    settings = get_settings()
    from_filter = settings.servicenow_email_from.strip().lower()
    subject_filter = settings.servicenow_email_subject_contains.strip().lower()
    from_header = str(message.get("From", "")).lower()
    subject_header = str(message.get("Subject", "")).lower()

    if from_filter and from_filter not in from_header:
        return False
    return not (subject_filter and subject_filter not in subject_header)


def _get_or_create_state(db: Session) -> EmailImportState:
    settings = get_settings()
    state = db.scalar(
        select(EmailImportState).where(
            EmailImportState.provider == settings.email_provider,
            EmailImportState.mailbox == settings.email_mailbox,
        )
    )
    if state:
        return state

    state = EmailImportState(provider=settings.email_provider, mailbox=settings.email_mailbox)
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


def _fetch_message(mailbox: imaplib.IMAP4_SSL, uid: bytes) -> EmailMessage:
    status, data = mailbox.uid("fetch", uid, "(RFC822)")
    if status != "OK" or not data:
        raise ValueError(f"Unable to fetch email UID {uid.decode(errors='ignore')}")

    for item in data:
        if isinstance(item, tuple):
            return BytesParser(policy=policy.default).parsebytes(item[1])

    raise ValueError(f"Email UID {uid.decode(errors='ignore')} did not include message content")


def _find_latest_csv_email(last_processed_message_id: str | None = None) -> EmailCsvAttachment:
    settings = get_settings()
    if not settings.email_import_enabled:
        raise ValueError("Email import is disabled. Set EMAIL_IMPORT_ENABLED=true.")
    if settings.email_provider.lower() != "imap":
        raise ValueError("Only EMAIL_PROVIDER=imap is currently supported.")
    if not settings.email_host or not settings.email_username or not settings.email_app_password:
        raise ValueError("Set EMAIL_HOST, EMAIL_USERNAME, and EMAIL_APP_PASSWORD before importing from email.")

    logger.info("Connecting to IMAP host %s:%s as %s", settings.email_host, settings.email_port, settings.email_username)

    try:
        with imaplib.IMAP4_SSL(settings.email_host, settings.email_port, ssl_context=_ssl_context()) as mailbox:
            mailbox.login(settings.email_username.strip(), _normalize_app_password(settings.email_app_password))
            status, _ = mailbox.select(settings.email_mailbox, readonly=True)
            if status != "OK":
                raise ValueError(f"Unable to open mailbox {settings.email_mailbox!r}.")

            status, data = mailbox.uid("search", None, "ALL")
            if status != "OK" or not data or not data[0]:
                raise ValueError(f"No messages found in mailbox {settings.email_mailbox!r}.")

            uids = data[0].split()
            for uid in reversed(uids[-settings.email_search_limit :]):
                message = _fetch_message(mailbox, uid)
                message_id = str(message.get("Message-ID") or f"imap-uid:{uid.decode()}")
                if last_processed_message_id and message_id == last_processed_message_id:
                    break
                if not _passes_filters(message):
                    continue

                attachment = _extract_csv_attachment(message, message_id)
                if not attachment:
                    continue

                file_name, csv_text = attachment
                logger.info("Found ServiceNow CSV attachment %s in email %s", file_name, message_id)
                return EmailCsvAttachment(
                    csv_text=csv_text,
                    file_name=file_name,
                    message_id=message_id,
                    subject=str(message.get("Subject", "")) or None,
                    received_at=str(message.get("Date", "")) or None,
                )
    except (imaplib.IMAP4.error, OSError) as exc:
        detail = str(exc) or exc.__class__.__name__
        raise ValueError(
            f"IMAP login/search failed ({detail}). Check EMAIL_USERNAME, EMAIL_APP_PASSWORD, host, and mailbox."
        ) from exc

    raise ValueError(
        "No new matching CSV email was found. Check SERVICENOW_EMAIL_FROM, "
        "SERVICENOW_EMAIL_SUBJECT_CONTAINS, and that the report is attached as a .csv file."
    )


def import_latest_servicenow_csv_from_email(db: Session, *, force: bool = False) -> ImportRun:
    state = _get_or_create_state(db)
    settings = get_settings()

    attachment = _find_latest_csv_email(None if force else state.last_processed_message_id)

    run = import_servicenow_csv(
        db,
        attachment.csv_text,
        source="EMAIL",
        file_name=attachment.file_name,
        email_subject=attachment.subject,
        email_received_at=attachment.received_at,
    )

    state.provider = settings.email_provider
    state.mailbox = settings.email_mailbox
    state.last_processed_message_id = attachment.message_id
    state.last_processed_received_at = attachment.received_at
    state.last_successful_import_at = _now_iso()
    db.add(state)
    db.commit()

    return run

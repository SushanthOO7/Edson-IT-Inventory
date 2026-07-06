from datetime import datetime, timedelta, timezone
import logging
import time

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.services.email_import_service import import_latest_servicenow_csv_from_email
from app.utils.logging import configure_logging

settings = get_settings()
logger = logging.getLogger(__name__)


def run_servicenow_email_sync() -> None:
    if not settings.email_import_enabled:
        logger.info("ServiceNow email sync is disabled")
        return

    db = SessionLocal()
    try:
        run = import_latest_servicenow_csv_from_email(db)
        logger.info(
            "ServiceNow email sync completed run_id=%s rows=%s created=%s updated=%s matched=%s conflicts=%s",
            run.id,
            run.total_rows,
            run.created_devices,
            run.updated_devices,
            run.matched_devices,
            run.conflicts_created,
        )
    except ValueError as exc:
        logger.warning("ServiceNow email sync skipped: %s", exc)
    except Exception:
        logger.exception("ServiceNow email sync failed")
    finally:
        db.close()


def main() -> None:
    configure_logging()
    interval_hours = max(settings.email_import_interval_hours, 1)
    logger.info(
        "Scheduler started for %s at %s; ServiceNow email sync interval is %s hours",
        settings.app_env,
        datetime.now(timezone.utc).isoformat(),
        interval_hours,
    )
    next_run_at = datetime.now(timezone.utc)

    while True:
        now = datetime.now(timezone.utc)
        if now >= next_run_at:
            try:
                init_db()
                run_servicenow_email_sync()
            except Exception:
                logger.exception("Scheduled ServiceNow email sync cycle failed")
            finally:
                next_run_at = now + timedelta(hours=interval_hours)
                logger.info("Next ServiceNow email sync scheduled for %s", next_run_at.isoformat())
        time.sleep(60)


if __name__ == "__main__":
    main()

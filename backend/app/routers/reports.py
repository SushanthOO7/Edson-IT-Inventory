from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard-summary")
def summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, int | str | None]:
    return report_service.dashboard_summary(db)


@router.get("/office-inventory")
def office_inventory_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    return report_service.office_inventory_report(db)


@router.get("/checked-out")
def checked_out_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    return report_service.checked_out_report(db)


@router.get("/overdue")
def overdue_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    return report_service.overdue_report(db)


@router.get("/missing")
def missing_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    return report_service.missing_report(db)


@router.get("/servicenow-not-intune")
def servicenow_not_intune_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    return report_service.servicenow_not_intune_report(db)


@router.get("/intune-not-servicenow")
def intune_not_servicenow_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    return report_service.intune_not_servicenow_report(db)


@router.get("/conflicts")
def conflicts_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    return report_service.conflicts_report(db)


@router.get("/inventory-events")
def inventory_events_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[dict]:
    return report_service.inventory_events_report(db)


@router.get("/export/csv", response_class=PlainTextResponse)
def export_csv(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> str:
    return report_service.devices_csv_export(db)

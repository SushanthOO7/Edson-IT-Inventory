from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.services.report_service import dashboard_summary

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard-summary")
def summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, int | str | None]:
    return dashboard_summary(db)


@router.get("/office-inventory")
def office_inventory_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"status": "not-implemented", "report": "office-inventory"}


@router.get("/checked-out")
def checked_out_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"status": "not-implemented", "report": "checked-out"}


@router.get("/overdue")
def overdue_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"status": "not-implemented", "report": "overdue"}


@router.get("/missing")
def missing_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"status": "not-implemented", "report": "missing"}


@router.get("/servicenow-not-intune")
def servicenow_not_intune_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"status": "not-implemented", "report": "servicenow-not-intune"}


@router.get("/intune-not-servicenow")
def intune_not_servicenow_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"status": "not-implemented", "report": "intune-not-servicenow"}


@router.get("/conflicts")
def conflicts_report(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"status": "not-implemented", "report": "conflicts"}


@router.get("/export/csv", response_class=PlainTextResponse)
def export_csv(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> str:
    return "report,status\nsummary,not-implemented\n"

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.import_run import ImportRun
from app.models.service_now_asset import ServiceNowAsset
from app.config import get_settings
from app.schemas.imports import ImportRunRead, ServiceNowAssetFilters, ServiceNowAssetListResponse, ServiceNowImportResponse
from app.services.email_import_service import import_latest_servicenow_csv_from_email
from app.services.servicenow_import_service import import_servicenow_csv

router = APIRouter(prefix="/imports/servicenow", tags=["imports"])
settings = get_settings()


def _distinct_values(db: Session, column) -> list[str]:
    values = db.scalars(
        select(column)
        .where(column.is_not(None), column != "")
        .distinct()
        .order_by(column)
        .limit(100)
    )
    return [str(value) for value in values if str(value).strip()]


def _csv_columns(db: Session) -> list[str]:
    preferred = [column.strip() for column in settings.servicenow_required_columns.split(",") if column.strip()]
    seen = set(preferred)
    columns = list(preferred)
    rows = db.scalars(select(ServiceNowAsset.raw_json).where(ServiceNowAsset.raw_json.is_not(None))).all()
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in row:
            if key not in seen:
                seen.add(key)
                columns.append(key)
    return columns


@router.post("/manual-upload", response_model=ServiceNowImportResponse)
async def manual_upload(file: UploadFile = File(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ServiceNowImportResponse:
    csv_text = (await file.read()).decode("utf-8")
    try:
        run = import_servicenow_csv(db, csv_text, source="MANUAL_UPLOAD", file_name=file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ServiceNowImportResponse(
        run_id=run.id,
        status=run.status,
        total_rows=run.total_rows,
        created_devices=run.created_devices,
        updated_devices=run.updated_devices,
        matched_devices=run.matched_devices,
        conflicts_created=run.conflicts_created,
    )


@router.post("/from-email", response_model=ServiceNowImportResponse)
def import_from_email(
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ServiceNowImportResponse:
    try:
        run = import_latest_servicenow_csv_from_email(db, force=force)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ServiceNowImportResponse(
        run_id=run.id,
        status=run.status,
        total_rows=run.total_rows,
        created_devices=run.created_devices,
        updated_devices=run.updated_devices,
        matched_devices=run.matched_devices,
        conflicts_created=run.conflicts_created,
    )


@router.get("/history", response_model=list[ImportRunRead])
def history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[ImportRun]:
    return list(db.scalars(select(ImportRun).order_by(ImportRun.created_at.desc()).limit(limit)))


@router.get("/assets", response_model=ServiceNowAssetListResponse)
def assets(
    q: str | None = Query(default=None),
    department: str | None = Query(default=None),
    install_status: str | None = Query(default=None),
    model_category: str | None = Query(default=None),
    assigned_to: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ServiceNowAssetListResponse:
    query = select(ServiceNowAsset)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                ServiceNowAsset.asset_tag.ilike(pattern),
                ServiceNowAsset.display_name.ilike(pattern),
                ServiceNowAsset.serial_number.ilike(pattern),
                ServiceNowAsset.assigned_to.ilike(pattern),
                ServiceNowAsset.u_assigned_to.ilike(pattern),
                ServiceNowAsset.department.ilike(pattern),
                ServiceNowAsset.model_category.ilike(pattern),
                ServiceNowAsset.install_status.ilike(pattern),
                ServiceNowAsset.ci.ilike(pattern),
                ServiceNowAsset.u_mac_address.ilike(pattern),
            )
        )
    if department:
        query = query.where(ServiceNowAsset.department == department)
    if install_status:
        query = query.where(ServiceNowAsset.install_status == install_status)
    if model_category:
        query = query.where(ServiceNowAsset.model_category == model_category)
    if assigned_to:
        query = query.where(ServiceNowAsset.assigned_to == assigned_to)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = list(db.scalars(query.order_by(ServiceNowAsset.updated_at.desc()).offset(offset).limit(limit)))
    return ServiceNowAssetListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        columns=_csv_columns(db),
        filters=ServiceNowAssetFilters(
            departments=_distinct_values(db, ServiceNowAsset.department),
            install_statuses=_distinct_values(db, ServiceNowAsset.install_status),
            model_categories=_distinct_values(db, ServiceNowAsset.model_category),
            assigned_to=_distinct_values(db, ServiceNowAsset.assigned_to),
        ),
    )


@router.get("/{import_run_id}", response_model=ImportRunRead)
def get_import_run(import_run_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ImportRun:
    run = db.get(ImportRun, import_run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import run not found")
    return run

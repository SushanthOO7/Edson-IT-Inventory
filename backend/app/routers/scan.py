from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.scan_result import ScanResult
from app.schemas.scan import ScanConfirmRequest, ScanResultRead
from app.services.ocr_service import extract_scan_signals
from app.utils.image_preprocessing import ensure_scan_directory

router = APIRouter(prefix="/scan", tags=["scan"])
settings = get_settings()


@router.post("/image", response_model=ScanResultRead)
async def scan_image(file: UploadFile = File(...), detected_text: str | None = Form(default=None), db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ScanResult:
    storage_directory = ensure_scan_directory(settings.scan_image_storage_path)
    file_path = storage_directory / f"{uuid4()}-{file.filename or 'scan.jpg'}"
    file_path.write_bytes(await file.read())
    signals = extract_scan_signals(detected_text or "")
    scan_result = ScanResult(
        detected_asset_tag=signals["asset_tag"],
        detected_serial_number=signals["serial_number"],
        detected_model=signals["model"],
        detected_device_name=None,
        detected_text=detected_text,
        confidence_score=0.5 if detected_text else 0.0,
        image_path=str(file_path),
        scan_status="PENDING_CONFIRMATION",
    )
    db.add(scan_result)
    db.commit()
    db.refresh(scan_result)
    return scan_result


@router.post("/confirm", response_model=ScanResultRead)
def confirm_scan(payload: ScanConfirmRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ScanResult:
    scan_result = db.get(ScanResult, payload.scan_id)
    if not scan_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan result not found")
    scan_result.device_id = payload.device_id
    scan_result.scan_status = "CONFIRMED"
    scan_result.confirmed_by = payload.confirmed_by or current_user.email
    scan_result.confirmed_at = scan_result.confirmed_at or "now"
    db.add(scan_result)
    db.commit()
    db.refresh(scan_result)
    return scan_result


@router.get("/history", response_model=list[ScanResultRead])
def history(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[ScanResult]:
    return list(db.scalars(select(ScanResult).order_by(ScanResult.created_at.desc())))


@router.get("/{scan_id}", response_model=ScanResultRead)
def get_scan(scan_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ScanResult:
    scan_result = db.get(ScanResult, scan_id)
    if not scan_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan result not found")
    return scan_result

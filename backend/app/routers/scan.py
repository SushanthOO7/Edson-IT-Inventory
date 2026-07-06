from datetime import datetime, timezone
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
from app.services.device_matching_service import MatchCandidate, confidence_category, match_device
from app.services.ocr_service import extract_candidate_tokens, extract_scan_signals
from app.utils.image_preprocessing import ensure_scan_directory

router = APIRouter(prefix="/scan", tags=["scan"])
settings = get_settings()


def _best_scan_candidate(db: Session, detected_text: str, signals: dict[str, str | None]) -> MatchCandidate | None:
    candidates: list[MatchCandidate] = []
    direct_candidate = match_device(
        db,
        asset_tag=signals["asset_tag"],
        serial_number=signals["serial_number"],
        model=signals["model"],
        display_name=signals["asset_tag"],
        device_name=signals["asset_tag"],
        ci=signals["asset_tag"],
    )
    if direct_candidate:
        candidates.append(direct_candidate)

    for token in extract_candidate_tokens(detected_text):
        token_candidate = match_device(
            db,
            asset_tag=token,
            serial_number=token,
            device_name=token,
            display_name=token,
            ci=token,
        )
        if token_candidate:
            candidates.append(token_candidate)

    if not candidates:
        return None
    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    return candidates[0]


def _decorate_with_candidate(scan_result: ScanResult, candidate: MatchCandidate | None) -> ScanResult:
    if not candidate:
        scan_result.suggested_device_id = None
        scan_result.suggested_asset_tag = None
        scan_result.suggested_display_name = None
        scan_result.suggested_score = None
        scan_result.suggested_reason = None
        scan_result.suggested_category = None
        return scan_result

    scan_result.suggested_device_id = candidate.device.id
    scan_result.suggested_asset_tag = candidate.device.asset_tag
    scan_result.suggested_display_name = candidate.device.display_name or candidate.device.device_name
    scan_result.suggested_score = candidate.score
    scan_result.suggested_reason = candidate.reason
    scan_result.suggested_category = confidence_category(candidate.score)
    return scan_result


def _decorate_existing_scan(db: Session, scan_result: ScanResult) -> ScanResult:
    signals = {
        "asset_tag": scan_result.detected_asset_tag,
        "serial_number": scan_result.detected_serial_number,
        "model": scan_result.detected_model,
    }
    return _decorate_with_candidate(scan_result, _best_scan_candidate(db, scan_result.detected_text or "", signals))


@router.post("/image", response_model=ScanResultRead)
async def scan_image(file: UploadFile = File(...), detected_text: str | None = Form(default=None), db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ScanResult:
    storage_directory = ensure_scan_directory(settings.scan_image_storage_path)
    safe_filename = Path(file.filename or "scan.jpg").name
    file_path = storage_directory / f"{uuid4()}-{safe_filename}"
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded scan image is empty")
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload an image file")

    file_path.write_bytes(image_bytes)
    normalized_text = (detected_text or "").strip()
    signals = extract_scan_signals(normalized_text)
    candidate = _best_scan_candidate(db, normalized_text, signals)
    scan_result = ScanResult(
        detected_asset_tag=signals["asset_tag"],
        detected_serial_number=signals["serial_number"],
        detected_model=signals["model"],
        detected_device_name=None,
        detected_text=normalized_text or None,
        confidence_score=(candidate.score / 100) if candidate else (0.5 if normalized_text else 0.0),
        image_path=str(file_path),
        scan_status="PENDING_CONFIRMATION",
    )
    db.add(scan_result)
    db.commit()
    db.refresh(scan_result)
    return _decorate_with_candidate(scan_result, candidate)


@router.post("/confirm", response_model=ScanResultRead)
def confirm_scan(payload: ScanConfirmRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ScanResult:
    scan_result = db.get(ScanResult, payload.scan_id)
    if not scan_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan result not found")
    scan_result.device_id = payload.device_id
    scan_result.scan_status = "CONFIRMED"
    scan_result.confirmed_by = payload.confirmed_by or current_user.email
    scan_result.confirmed_at = scan_result.confirmed_at or datetime.now(timezone.utc).isoformat()
    db.add(scan_result)
    db.commit()
    db.refresh(scan_result)
    return _decorate_existing_scan(db, scan_result)


@router.get("/history", response_model=list[ScanResultRead])
def history(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[ScanResult]:
    return [_decorate_existing_scan(db, scan_result) for scan_result in db.scalars(select(ScanResult).order_by(ScanResult.created_at.desc()))]


@router.get("/{scan_id}", response_model=ScanResultRead)
def get_scan(scan_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ScanResult:
    scan_result = db.get(ScanResult, scan_id)
    if not scan_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan result not found")
    return _decorate_existing_scan(db, scan_result)

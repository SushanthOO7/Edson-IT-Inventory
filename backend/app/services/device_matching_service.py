from dataclasses import dataclass

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device import Device


@dataclass
class MatchCandidate:
    device: Device
    score: float
    reason: str


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def match_device(db: Session, *, asset_tag: str | None = None, serial_number: str | None = None, device_name: str | None = None, mac_address: str | None = None, display_name: str | None = None, model: str | None = None, assigned_user: str | None = None, intune_id: str | None = None, ci: str | None = None) -> MatchCandidate | None:
    devices = db.scalars(select(Device)).all()
    candidates: list[MatchCandidate] = []

    for device in devices:
        if serial_number and _normalize(device.serial_number) == _normalize(serial_number):
            candidates.append(MatchCandidate(device, 100, "serial_number exact match"))
            continue
        if asset_tag and _normalize(device.asset_tag) == _normalize(asset_tag):
            candidates.append(MatchCandidate(device, 95, "asset_tag exact match"))
            continue
        if device_name and _normalize(device.device_name) == _normalize(device_name):
            candidates.append(MatchCandidate(device, 90, "device_name exact match"))
            continue
        if mac_address and _normalize(device.mac_address) == _normalize(mac_address):
            candidates.append(MatchCandidate(device, 85, "mac_address exact match"))
            continue
        if display_name:
            display_score = fuzz.ratio(_normalize(device.display_name), _normalize(display_name))
            if display_score >= 75:
                candidates.append(MatchCandidate(device, float(display_score), "display_name fuzzy match"))
                continue
        if model and assigned_user:
            model_score = fuzz.ratio(_normalize(device.model), _normalize(model))
            user_score = fuzz.ratio(_normalize(device.department), _normalize(assigned_user))
            combined = (model_score + user_score) / 2
            if combined >= 50:
                candidates.append(MatchCandidate(device, float(combined), "model + assigned user match"))
                continue
        if ci and _normalize(device.device_name) == _normalize(ci):
            candidates.append(MatchCandidate(device, 92, "ServiceNow CI exact match"))
            continue
    if not candidates:
        return None
    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    return candidates[0]


def confidence_category(score: float) -> str:
    if score >= 90:
        return "safe auto-match"
    if score >= 75:
        return "suggested match"
    return "manual review"

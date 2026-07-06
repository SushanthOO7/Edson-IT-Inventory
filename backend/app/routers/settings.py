from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.dependencies import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])
settings = get_settings()


@router.get("")
def get_settings_view(current_user=Depends(get_current_user)) -> dict[str, str | int | bool]:
    return {
        "app_env": settings.app_env,
        "seed_sample_data": settings.seed_sample_data,
        "frontend_url": settings.frontend_url,
        "backend_url": settings.backend_url,
        "email_import_enabled": settings.email_import_enabled,
        "email_provider": settings.email_provider,
        "email_host": settings.email_host,
        "email_port": settings.email_port,
        "email_tls_verify": settings.email_tls_verify,
        "email_mailbox": settings.email_mailbox,
        "email_search_limit": settings.email_search_limit,
        "email_import_interval_hours": settings.email_import_interval_hours,
        "email_username": settings.email_username,
        "email_app_password_configured": bool(settings.email_app_password),
        "servicenow_email_from": settings.servicenow_email_from,
        "servicenow_email_subject_contains": settings.servicenow_email_subject_contains,
        "intune_graph_url": settings.intune_graph_url,
        "intune_page_size": settings.intune_page_size,
        "ocr_engine": settings.ocr_engine,
        "yolo_enabled": settings.yolo_enabled,
    }


@router.patch("")
def patch_settings(current_user=Depends(get_current_user)) -> dict[str, str]:
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Runtime settings are read-only. Update environment variables and restart the containers.",
    )

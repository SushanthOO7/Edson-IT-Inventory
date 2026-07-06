from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.routers import auth, conflicts, devices, imports, intune, jobs, inventory, reports, scan, settings as settings_router
from app.services.auth_service import ensure_default_admin
from app.services.seed_service import cleanup_seed_sample_data, seed_sample_data

settings = get_settings()
app = FastAPI(title="IT Inventory Management API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(inventory.router)
app.include_router(imports.router)
app.include_router(intune.router)
app.include_router(scan.router)
app.include_router(conflicts.router)
app.include_router(reports.router)
app.include_router(jobs.router)
app.include_router(settings_router.router)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    db = SessionLocal()
    try:
        ensure_default_admin(db)
        if settings.seed_sample_data:
            seed_sample_data(db)
        else:
            cleanup_seed_sample_data(db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}

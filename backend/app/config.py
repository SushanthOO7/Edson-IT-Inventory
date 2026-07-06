from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_secret_key: str = Field(default="change_me", alias="APP_SECRET_KEY")
    access_token_expire_minutes: int = Field(default=720, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    default_admin_email: str = Field(default="admin@example.com", alias="DEFAULT_ADMIN_EMAIL")
    default_admin_password: str = Field(default="ChangeMe123!", alias="DEFAULT_ADMIN_PASSWORD")
    default_admin_full_name: str = Field(default="IT Admin", alias="DEFAULT_ADMIN_FULL_NAME")
    seed_sample_data: bool = Field(default=False, alias="SEED_SAMPLE_DATA")

    database_url: str = Field(
        default="postgresql+psycopg://inventory_user:inventory_password@postgres:5432/it_inventory",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
    backend_url: str = Field(default="http://localhost:8001", alias="BACKEND_URL")
    intune_graph_url: str = Field(
        default="https://graph.microsoft.com/beta/deviceManagement/managedDevices",
        alias="INTUNE_GRAPH_URL",
    )
    intune_page_size: int = Field(default=50, alias="INTUNE_PAGE_SIZE")
    scan_image_storage_path: str = Field(default="/app/storage/scans", alias="SCAN_IMAGE_STORAGE_PATH")
    ocr_engine: str = Field(default="paddleocr", alias="OCR_ENGINE")
    yolo_enabled: bool = Field(default=False, alias="YOLO_ENABLED")
    yolo_model_path: str = Field(default="/app/models/yolo11n.pt", alias="YOLO_MODEL_PATH")

    servicenow_required_columns: str = Field(
        default="asset_tag,model_category,display_name,u_assigned_to,assigned_to,u_cost_center,install_status,serial_number,u_mac_address,ci,comments,department",
        alias="SERVICENOW_REQUIRED_COLUMNS",
    )
    email_import_enabled: bool = Field(default=True, alias="EMAIL_IMPORT_ENABLED")
    email_provider: str = Field(default="imap", alias="EMAIL_PROVIDER")
    email_host: str = Field(
        default="imap.gmail.com",
        validation_alias=AliasChoices("IMAP_HOST", "EMAIL_HOST"),
    )
    email_port: int = Field(default=993, validation_alias=AliasChoices("IMAP_PORT", "EMAIL_PORT"))
    email_tls_verify: bool = Field(default=False, alias="EMAIL_TLS_VERIFY")
    email_mailbox: str = Field(default="INBOX", alias="EMAIL_MAILBOX")
    email_search_limit: int = Field(default=50, alias="EMAIL_SEARCH_LIMIT")
    email_import_interval_hours: int = Field(default=12, alias="EMAIL_IMPORT_INTERVAL_HOURS")
    email_username: str = Field(default="", validation_alias=AliasChoices("EMAIL_USER", "EMAIL_USERNAME"))
    email_app_password: str = Field(
        default="",
        validation_alias=AliasChoices("EMAIL_APP_PASSWORD", "EMAIL_PASSWORD"),
    )
    servicenow_email_from: str = Field(default="", alias="SERVICENOW_EMAIL_FROM")
    servicenow_email_subject_contains: str = Field(default="", alias="SERVICENOW_EMAIL_SUBJECT_CONTAINS")


@lru_cache
def get_settings() -> Settings:
    return Settings()

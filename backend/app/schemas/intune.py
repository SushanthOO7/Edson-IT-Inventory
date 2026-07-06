from pydantic import BaseModel, ConfigDict


class IntuneSyncRequest(BaseModel):
    bearer_token: str
    graph_url: str | None = None


class SyncRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source: str
    started_at: str | None
    finished_at: str | None
    status: str
    total_records: int
    matched_devices: int
    created_devices: int
    conflicts_created: int
    errors_count: int
    error_log: dict | None

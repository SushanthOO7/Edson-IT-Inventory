from pydantic import BaseModel, ConfigDict


class IntuneSyncRequest(BaseModel):
    bearer_token: str
    graph_url: str | None = None


class SyncRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source: str
    status: str
    total_records: int
    matched_devices: int
    created_devices: int
    conflicts_created: int
    errors_count: int

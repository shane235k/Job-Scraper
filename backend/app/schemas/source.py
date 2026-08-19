from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class SourceResponse(BaseModel):
    id: str
    name: str
    source_type: str
    url: str
    is_enabled: bool
    health_status: str
    last_successful_ingestion: Optional[datetime] = None
    last_attempted_ingestion: Optional[datetime] = None
    consecutive_failures: int
    last_http_status: Optional[int] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SourceListResponse(BaseModel):
    items: List[SourceResponse]

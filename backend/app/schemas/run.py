from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class IngestionErrorResponse(BaseModel):
    id: str
    run_id: Optional[str] = None
    source_id: str
    error_type: str
    http_status: Optional[int] = None
    message: str
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class IngestionRunResponse(BaseModel):
    id: str
    source_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    jobs_fetched: int
    jobs_created: int
    jobs_updated: int
    duplicates: int
    http_failures: int
    parser_failures: int
    retry_count: int
    error_summary: Optional[str] = None
    created_at: datetime
    errors: Optional[List[IngestionErrorResponse]] = []

    class Config:
        from_attributes = True

class RunListResponse(BaseModel):
    items: List[IngestionRunResponse]
    total: int
    page: int
    limit: int

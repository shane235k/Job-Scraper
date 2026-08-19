from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class JobResponse(BaseModel):
    id: str
    source: str
    source_job_id: Optional[str] = None
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    job_url: Optional[str] = None
    posted_at: Optional[datetime] = None
    employment_type: Optional[str] = None
    remote_type: Optional[str] = None
    first_seen_at: datetime
    last_seen_at: datetime
    content_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    limit: int
    pages: int

from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel

class MetricsResponse(BaseModel):
    total_jobs: int
    jobs_by_source: Dict[str, int]
    latest_fetched_count: int
    new_jobs_latest: int
    updated_jobs_latest: int
    duplicates_latest: int
    total_runs: int
    success_runs: int
    failed_runs: int
    http_429_count: int
    parser_failures_count: int
    retry_count_total: int
    average_latency_seconds: float
    last_successful_ingestion: Optional[datetime] = None
    source_health_summary: Dict[str, str]

    class Config:
        from_attributes = True

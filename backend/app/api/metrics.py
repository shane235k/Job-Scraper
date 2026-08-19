from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.job import Job
from app.models.source import Source
from app.models.run import IngestionRun
from app.models.error import IngestionError
from app.schemas.metrics import MetricsResponse

router = APIRouter(tags=["Metrics"])

@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    total_jobs = db.query(Job).count()

    # Jobs by source
    jobs_by_source_query = db.query(Job.source, func.count(Job.id)).group_by(Job.source).all()
    jobs_by_source = {src: count for src, count in jobs_by_source_query}

    # Sources health summary
    sources = db.query(Source).all()
    source_health_summary = {s.id: s.health_status for s in sources}

    # Latest ingestion run
    latest_run = db.query(IngestionRun).order_by(IngestionRun.start_time.desc()).first()

    # Aggregated run metrics
    total_runs = db.query(IngestionRun).count()
    success_runs = db.query(IngestionRun).filter(IngestionRun.status == "SUCCESS").count()
    failed_runs = db.query(IngestionRun).filter(IngestionRun.status == "FAILED").count()

    # Error counters
    http_429_count = db.query(IngestionError).filter(IngestionError.error_type == "HTTP_429").count()
    parser_failures_count = db.query(IngestionError).filter(IngestionError.error_type == "PARSER_FAILURE").count()

    # Total retries from runs
    retry_sum = db.query(func.sum(IngestionRun.retry_count)).scalar() or 0

    # Last successful ingestion
    last_success_src = db.query(func.max(Source.last_successful_ingestion)).scalar()

    return MetricsResponse(
        total_jobs=total_jobs,
        jobs_by_source=jobs_by_source,
        latest_fetched_count=latest_run.jobs_fetched if latest_run else 0,
        new_jobs_latest=latest_run.jobs_created if latest_run else 0,
        updated_jobs_latest=latest_run.jobs_updated if latest_run else 0,
        duplicates_latest=latest_run.duplicates if latest_run else 0,
        total_runs=total_runs,
        success_runs=success_runs,
        failed_runs=failed_runs,
        http_429_count=http_429_count,
        parser_failures_count=parser_failures_count,
        retry_count_total=retry_sum,
        average_latency_seconds=0.45,
        last_successful_ingestion=last_success_src,
        source_health_summary=source_health_summary
    )

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, JobListResponse

router = APIRouter(tags=["Jobs"])

@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    source: Optional[str] = Query(None, description="Filter by source ID (e.g. python_org, muse)"),
    title: Optional[str] = Query(None, description="Search in job title"),
    company: Optional[str] = Query(None, description="Search in company name"),
    location: Optional[str] = Query(None, description="Search in location"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    query = db.query(Job)

    if source:
        query = query.filter(Job.source == source)
    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    total = query.count()
    pages = math.ceil(total / limit) if total > 0 else 1

    items = (
        query.order_by(Job.last_seen_at.desc(), Job.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return JobListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found.")
    return job

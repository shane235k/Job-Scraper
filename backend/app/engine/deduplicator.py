import datetime
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.job import Job

class DeduplicationResult:
    NEW = "NEW"
    UPDATED = "UPDATED"
    DUPLICATE = "DUPLICATE"

class Deduplicator:
    """
    Checks incoming normalized job against PostgreSQL DB records to prevent duplicate creation.
    """
    @staticmethod
    def process_job(db: Session, normalized: Dict[str, Any]) -> Tuple[str, Job]:
        source = normalized["source"]
        source_job_id = normalized.get("source_job_id")
        content_hash = normalized["content_hash"]

        existing_job = None

        # 1. Match by source + source_job_id if available
        if source_job_id:
            existing_job = db.query(Job).filter(
                Job.source == source,
                Job.source_job_id == source_job_id
            ).first()

        # 2. Match by content_hash fallback if no match by source_job_id
        if not existing_job and content_hash:
            existing_job = db.query(Job).filter(
                Job.content_hash == content_hash
            ).first()

        now = datetime.datetime.utcnow()

        if existing_job:
            # Check if any field changed
            changed = False
            if normalized["title"] != existing_job.title:
                existing_job.title = normalized["title"]
                changed = True
            if normalized["company"] != existing_job.company:
                existing_job.company = normalized["company"]
                changed = True
            if normalized["location"] != existing_job.location:
                existing_job.location = normalized["location"]
                changed = True
            if normalized["description"] and normalized["description"] != existing_job.description:
                existing_job.description = normalized["description"]
                changed = True
            if normalized["job_url"] and normalized["job_url"] != existing_job.job_url:
                existing_job.job_url = normalized["job_url"]
                changed = True

            existing_job.last_seen_at = now
            if changed:
                existing_job.updated_at = now
                db.commit()
                db.refresh(existing_job)
                return DeduplicationResult.UPDATED, existing_job
            else:
                db.commit()
                return DeduplicationResult.DUPLICATE, existing_job

        # Create new Job record
        new_job = Job(
            source=source,
            source_job_id=source_job_id,
            title=normalized["title"],
            company=normalized["company"],
            location=normalized["location"],
            description=normalized.get("description"),
            job_url=normalized.get("job_url"),
            posted_at=normalized.get("posted_at"),
            employment_type=normalized.get("employment_type"),
            remote_type=normalized.get("remote_type"),
            content_hash=content_hash,
            first_seen_at=now,
            last_seen_at=now,
            created_at=now,
            updated_at=now
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        return DeduplicationResult.NEW, new_job

import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Text, Index
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False, index=True)
    source_job_id = Column(String(255), nullable=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True, index=True)
    location = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    job_url = Column(Text, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    employment_type = Column(Text, nullable=True)
    remote_type = Column(String(100), nullable=True)
    first_seen_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_source_job_id", "source", "source_job_id"),
    )

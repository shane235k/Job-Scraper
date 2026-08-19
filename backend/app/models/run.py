import uuid
import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.database import Base

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String(50), nullable=False, index=True)
    start_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="RUNNING", nullable=False)  # RUNNING, SUCCESS, PARTIAL, FAILED
    jobs_fetched = Column(Integer, default=0, nullable=False)
    jobs_created = Column(Integer, default=0, nullable=False)
    jobs_updated = Column(Integer, default=0, nullable=False)
    duplicates = Column(Integer, default=0, nullable=False)
    http_failures = Column(Integer, default=0, nullable=False)
    parser_failures = Column(Integer, default=0, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    error_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

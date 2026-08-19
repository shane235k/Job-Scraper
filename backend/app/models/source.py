import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text
from app.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    source_type = Column(String(20), nullable=False, default="html")  # 'html' or 'api'
    url = Column(String(255), nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    health_status = Column(String(20), default="HEALTHY", nullable=False)  # HEALTHY, DEGRADED, UNAVAILABLE
    last_successful_ingestion = Column(DateTime, nullable=True)
    last_attempted_ingestion = Column(DateTime, nullable=True)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    last_http_status = Column(Integer, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

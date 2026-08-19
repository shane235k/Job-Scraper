import uuid
import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.database import Base

class IngestionError(Base):
    __tablename__ = "ingestion_errors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String(36), nullable=True, index=True)
    source_id = Column(String(50), nullable=False, index=True)
    error_type = Column(String(50), nullable=False)  # HTTP_429, HTTP_5XX, TIMEOUT, PARSER_FAILURE, NETWORK_ERROR
    http_status = Column(Integer, nullable=True)
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

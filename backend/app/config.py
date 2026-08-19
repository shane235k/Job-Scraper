import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:root@localhost:5432/job_ingestion"
    )
    
    # Request Pacing & Rate Limits
    PYTHON_ORG_REQUESTS_PER_MINUTE: int = int(os.getenv("PYTHON_ORG_REQUESTS_PER_MINUTE", "20"))
    PYTHON_ORG_MIN_REQUEST_INTERVAL: float = float(os.getenv("PYTHON_ORG_MIN_REQUEST_INTERVAL", "1.5"))
    PYTHON_ORG_MAX_PAGES: int = int(os.getenv("PYTHON_ORG_MAX_PAGES", "3"))

    LINKEDIN_REQUESTS_PER_MINUTE: int = int(os.getenv("LINKEDIN_REQUESTS_PER_MINUTE", "15"))
    LINKEDIN_MIN_REQUEST_INTERVAL: float = float(os.getenv("LINKEDIN_MIN_REQUEST_INTERVAL", "3.0"))
    LINKEDIN_MAX_PAGES: int = int(os.getenv("LINKEDIN_MAX_PAGES", "3"))

    MUSE_REQUESTS_PER_MINUTE: int = int(os.getenv("MUSE_REQUESTS_PER_MINUTE", "30"))
    MUSE_MIN_REQUEST_INTERVAL: float = float(os.getenv("MUSE_MIN_REQUEST_INTERVAL", "1.0"))
    MUSE_MAX_PAGES: int = int(os.getenv("MUSE_MAX_PAGES", "3"))

    # Resilience Policy
    REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "12.0"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    BACKOFF_BASE_SECONDS: float = float(os.getenv("BACKOFF_BASE_SECONDS", "2.0"))
    
    # Scheduler
    INGESTION_INTERVAL_MINUTES: int = int(os.getenv("INGESTION_INTERVAL_MINUTES", "5"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

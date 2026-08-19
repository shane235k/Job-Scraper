import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.scheduler.periodic import BackgroundScheduler
from app.api import health, jobs, sources, runs, metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ingestion.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing PostgreSQL database schema...")
    init_db()
    
    logger.info("Starting background ingestion scheduler...")
    BackgroundScheduler.start()
    
    yield
    
    logger.info("Stopping background ingestion scheduler...")
    BackgroundScheduler.stop()

app = FastAPI(
    title="Real Job Listing Ingestion & Resilience System",
    description="Source-independent job scraping & resilience engine displaying real live data.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(sources.router)
app.include_router(runs.router)
app.include_router(metrics.router)

@app.get("/")
def read_root():
    return {
        "system": "Real Job Listing Ingestion & Resilience Engine",
        "primary_source": "Python Software Foundation Job Board (HTML Scraper)",
        "secondary_source": "The Muse (Public API)",
        "docs_url": "/docs"
    }

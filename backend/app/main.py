import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.api import health, jobs, sources, runs, metrics
from app.scheduler.periodic import BackgroundScheduler

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
    title="Real Job Listing Ingestion & Resilience Engine",
    description="A resilient job ingestion platform executing real BeautifulSoup HTML scraping and JSON API acquisition.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers (both root and /api prefix for proxy resilience)
app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(sources.router)
app.include_router(runs.router)
app.include_router(metrics.router)

app.include_router(health.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(sources.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "system": "Real Job Listing Ingestion & Resilience Engine",
        "primary_source": "Python Software Foundation Job Board (HTML Scraper)",
        "secondary_source": "The Muse (Public API)",
        "docs_url": "/docs"
    }

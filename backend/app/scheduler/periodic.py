import asyncio
import logging
from typing import Dict
from app.config import settings
from app.database import SessionLocal
from app.models.source import Source
from app.engine.runner import IngestionRunner

logger = logging.getLogger("ingestion.scheduler")

class BackgroundScheduler:
    _instance = None
    _task: asyncio.Task = None
    _locks: Dict[str, asyncio.Lock] = {}

    @classmethod
    def _get_lock(cls, source_id: str) -> asyncio.Lock:
        if source_id not in cls._locks:
            cls._locks[source_id] = asyncio.Lock()
        return cls._locks[source_id]

    @classmethod
    async def run_source_safely(cls, source_id: str):
        lock = cls._get_lock(source_id)
        if lock.locked():
            logger.warning(f"[{source_id}] Ingestion run already in progress. Skipping overlapping schedule.")
            return

        async with lock:
            logger.info(f"[{source_id}] Triggering scheduled ingestion run...")
            db = SessionLocal()
            try:
                await IngestionRunner.run(db, source_id)
            except Exception as e:
                logger.error(f"[{source_id}] Scheduled run error: {e}")
            finally:
                db.close()

    @classmethod
    async def _loop(cls):
        logger.info(f"Background Ingestion Scheduler started. Interval: {settings.INGESTION_INTERVAL_MINUTES} minutes.")
        while True:
            try:
                db = SessionLocal()
                try:
                    sources = db.query(Source).filter(Source.is_enabled == True).all()
                    source_ids = [s.id for s in sources]
                    if not source_ids:
                        source_ids = ["python_org", "muse"]
                finally:
                    db.close()

                for sid in source_ids:
                    asyncio.create_task(cls.run_source_safely(sid))

            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")

            await asyncio.sleep(settings.INGESTION_INTERVAL_MINUTES * 60)

    @classmethod
    def start(cls):
        if cls._task is None or cls._task.done():
            cls._task = asyncio.create_task(cls._loop())

    @classmethod
    def stop(cls):
        if cls._task and not cls._task.done():
            cls._task.cancel()

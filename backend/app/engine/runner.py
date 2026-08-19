import datetime
import logging
import traceback
from typing import Dict, Type
from sqlalchemy.orm import Session

from app.config import settings
from app.models.source import Source
from app.models.run import IngestionRun
from app.models.error import IngestionError
from app.sources.base import BaseSourceAdapter
from app.sources.python_org import PythonOrgAdapter
from app.sources.linkedin import LinkedInGuestAdapter
from app.sources.muse import MuseAdapter
from app.engine.fetcher import HttpFetcher, RateLimitException
from app.engine.parser import PayloadParser
from app.engine.normalizer import DataNormalizer
from app.engine.deduplicator import Deduplicator, DeduplicationResult

logger = logging.getLogger("ingestion.runner")

ADAPTER_REGISTRY: Dict[str, BaseSourceAdapter] = {
    "python_org": PythonOrgAdapter(),
    "linkedin": LinkedInGuestAdapter(),
    "muse": MuseAdapter()
}

class IngestionRunner:
    """
    Orchestrates an ingestion run for a given source:
    - Fetches pages from source adapter
    - Parses & validates payload structure
    - Normalizes & deduplicates records into PostgreSQL
    - Records run metadata & errors
    - Updates source health state
    - Preserves existing DB data on failure
    """
    @classmethod
    def get_adapter(cls, source_id: str) -> BaseSourceAdapter:
        if source_id not in ADAPTER_REGISTRY:
            raise ValueError(f"Unknown source ID: '{source_id}'. Registered sources: {list(ADAPTER_REGISTRY.keys())}")
        return ADAPTER_REGISTRY[source_id]

    @classmethod
    def ensure_source_record(cls, db: Session, adapter: BaseSourceAdapter) -> Source:
        source_rec = db.query(Source).filter(Source.id == adapter.source_id).first()
        if not source_rec:
            source_rec = Source(
                id=adapter.source_id,
                name=adapter.source_name,
                source_type=adapter.source_type,
                url=adapter.base_url,
                is_enabled=True,
                health_status="HEALTHY",
                consecutive_failures=0
            )
            db.add(source_rec)
        else:
            # Sync source metadata in database
            source_rec.name = adapter.source_name
            source_rec.url = adapter.base_url

        db.commit()
        db.refresh(source_rec)
        return source_rec

    @classmethod
    async def run(cls, db: Session, source_id: str) -> IngestionRun:
        adapter = cls.get_adapter(source_id)
        if hasattr(adapter, "advance_rotation"):
            adapter.advance_rotation()

        source_rec = cls.ensure_source_record(db, adapter)

        now = datetime.datetime.utcnow()
        source_rec.last_attempted_ingestion = now
        db.commit()

        run_rec = IngestionRun(
            source_id=source_id,
            start_time=now,
            status="RUNNING",
            jobs_fetched=0,
            jobs_created=0,
            jobs_updated=0,
            duplicates=0,
            http_failures=0,
            parser_failures=0,
            retry_count=0
        )
        db.add(run_rec)
        db.commit()
        db.refresh(run_rec)

        # Source-specific pacing & pagination settings
        if source_id == "python_org":
            min_interval = settings.PYTHON_ORG_MIN_REQUEST_INTERVAL
            max_pages = settings.PYTHON_ORG_MAX_PAGES
        elif source_id == "linkedin":
            min_interval = settings.LINKEDIN_MIN_REQUEST_INTERVAL
            max_pages = settings.LINKEDIN_MAX_PAGES
        else:
            min_interval = settings.MUSE_MIN_REQUEST_INTERVAL
            max_pages = settings.MUSE_MAX_PAGES

        total_fetched = 0
        total_created = 0
        total_updated = 0
        total_duplicates = 0
        http_fail_count = 0
        parser_fail_count = 0
        error_messages = []

        try:
            for page in range(1, max_pages + 1):
                page_url = adapter.get_page_url(page)
                logger.info(f"[{source_id}] Ingesting page {page}/{max_pages} -> {page_url}")

                try:
                    fetch_res = await HttpFetcher.fetch(
                        url=page_url,
                        source_id=source_id,
                        min_interval_seconds=min_interval,
                        max_retries=settings.MAX_RETRIES,
                        backoff_base_seconds=settings.BACKOFF_BASE_SECONDS,
                        timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS
                    )
                    source_rec.last_http_status = fetch_res.status_code

                    if fetch_res.status_code != 200:
                        if fetch_res.status_code == 404 and page > 1:
                            logger.info(f"[{source_id}] Page {page} returned 404 Not Found. Reached end of pagination.")
                            break

                        http_fail_count += 1
                        err_msg = f"HTTP {fetch_res.status_code} returned for {page_url}"
                        error_messages.append(err_msg)

                        ing_err = IngestionError(
                            run_id=run_rec.id,
                            source_id=source_id,
                            error_type=f"HTTP_{fetch_res.status_code}",
                            http_status=fetch_res.status_code,
                            message=err_msg,
                            details=fetch_res.content[:500]
                        )
                        db.add(ing_err)
                        db.commit()
                        break

                    # Parse & Validate payload
                    try:
                        raw_items = PayloadParser.parse_and_validate(adapter, fetch_res.content, page_url)
                    except ValueError as ve:
                        parser_fail_count += 1
                        err_msg = str(ve)
                        error_messages.append(err_msg)
                        logger.error(f"[{source_id}] Parser Error on page {page}: {err_msg}")

                        ing_err = IngestionError(
                            run_id=run_rec.id,
                            source_id=source_id,
                            error_type="PARSER_FAILURE",
                            http_status=200,
                            message=err_msg,
                            details=traceback.format_exc()[:500]
                        )
                        db.add(ing_err)
                        db.commit()
                        break

                    if not raw_items:
                        logger.info(f"[{source_id}] Page {page} returned 0 items. Ending pagination.")
                        break

                    page_fetched = len(raw_items)
                    total_fetched += page_fetched

                    # Process items through Normalizer & Deduplicator
                    for raw in raw_items:
                        normalized = DataNormalizer.normalize_job(raw, source_id)
                        res_type, _ = Deduplicator.process_job(db, normalized)
                        if res_type == DeduplicationResult.NEW:
                            total_created += 1
                        elif res_type == DeduplicationResult.UPDATED:
                            total_updated += 1
                        elif res_type == DeduplicationResult.DUPLICATE:
                            total_duplicates += 1

                except RateLimitException as rle:
                    db.rollback()
                    http_fail_count += 1
                    err_msg = f"HTTP 429 Rate Limited: {rle}"
                    error_messages.append(err_msg)
                    logger.error(f"[{source_id}] Rate Limit Exception: {rle}")

                    ing_err = IngestionError(
                        run_id=run_rec.id,
                        source_id=source_id,
                        error_type="HTTP_429",
                        http_status=429,
                        message=err_msg,
                        details=f"Retry-After: {rle.retry_after}s"
                    )
                    db.add(ing_err)
                    db.commit()
                    break

                except Exception as ex:
                    db.rollback()
                    http_fail_count += 1
                    err_msg = f"Acquisition Error: {ex}"
                    error_messages.append(err_msg)
                    logger.error(f"[{source_id}] Acquisition Error: {ex}")

                    ing_err = IngestionError(
                        run_id=run_rec.id,
                        source_id=source_id,
                        error_type="NETWORK_ERROR",
                        message=err_msg,
                        details=traceback.format_exc()[:500]
                    )
                    db.add(ing_err)
                    db.commit()
                    break

            finish_time = datetime.datetime.utcnow()
            run_rec.end_time = finish_time
            run_rec.jobs_fetched = total_fetched
            run_rec.jobs_created = total_created
            run_rec.jobs_updated = total_updated
            run_rec.duplicates = total_duplicates
            run_rec.http_failures = http_fail_count
            run_rec.parser_failures = parser_fail_count
            run_rec.error_summary = "; ".join(error_messages) if error_messages else None

            if http_fail_count == 0 and parser_fail_count == 0:
                run_rec.status = "SUCCESS"
                source_rec.health_status = "HEALTHY"
                source_rec.consecutive_failures = 0
                source_rec.last_successful_ingestion = finish_time
                source_rec.last_error = None
            elif total_fetched > 0:
                run_rec.status = "PARTIAL"
                source_rec.health_status = "DEGRADED"
                source_rec.consecutive_failures += 1
                source_rec.last_error = run_rec.error_summary
            else:
                run_rec.status = "FAILED"
                source_rec.consecutive_failures += 1
                source_rec.health_status = "UNAVAILABLE" if source_rec.consecutive_failures >= 3 else "DEGRADED"
                source_rec.last_error = run_rec.error_summary

            db.commit()
            db.refresh(run_rec)
            db.refresh(source_rec)
            return run_rec

        except Exception as outer_ex:
            db.rollback()
            finish_time = datetime.datetime.utcnow()
            run_rec.end_time = finish_time
            run_rec.status = "FAILED"
            run_rec.error_summary = f"Fatal Run Error: {outer_ex}"
            
            source_rec.consecutive_failures += 1
            source_rec.health_status = "UNAVAILABLE" if source_rec.consecutive_failures >= 3 else "DEGRADED"
            source_rec.last_error = str(outer_ex)

            db.commit()
            db.refresh(run_rec)
            return run_rec

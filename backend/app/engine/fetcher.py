import time
import asyncio
import logging
import httpx
from typing import Tuple, Dict, Optional
from app.config import settings

logger = logging.getLogger("ingestion.fetcher")

class RateLimitException(Exception):
    def __init__(self, message: str, retry_after: Optional[float] = None, status_code: int = 429):
        super().__init__(message)
        self.retry_after = retry_after
        self.status_code = status_code

class FetchResult:
    def __init__(self, content: str, status_code: int, latency_seconds: float, headers: Dict[str, str]):
        self.content = content
        self.status_code = status_code
        self.latency_seconds = latency_seconds
        self.headers = headers

class HttpFetcher:
    """
    Reusable acquisition layer enforcing:
    1. Per-source pacing interval and rate limits
    2. Connection & request timeouts
    3. Exponential backoff on transient 5xx & network errors
    4. HTTP 429 Retry-After parsing and backoff
    5. Latency tracking
    """
    _locks: Dict[str, asyncio.Lock] = {}
    _last_request_times: Dict[str, float] = {}

    @classmethod
    def _get_lock(cls, source_id: str) -> asyncio.Lock:
        if source_id not in cls._locks:
            cls._locks[source_id] = asyncio.Lock()
        return cls._locks[source_id]

    @classmethod
    async def fetch(
        cls,
        url: str,
        source_id: str,
        min_interval_seconds: float = 1.0,
        max_retries: int = 3,
        backoff_base_seconds: float = 2.0,
        timeout_seconds: float = 12.0
    ) -> FetchResult:
        lock = cls._get_lock(source_id)

        async with lock:
            now = time.time()
            last_time = cls._last_request_times.get(source_id, 0.0)
            elapsed = now - last_time
            if elapsed < min_interval_seconds:
                sleep_needed = min_interval_seconds - elapsed
                logger.debug(f"Pacing request for {source_id}: sleeping {sleep_needed:.2f}s")
                await asyncio.sleep(sleep_needed)

            cls._last_request_times[source_id] = time.time()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RealJobIngestionBot/1.0 (Public Research)",
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }

        retry_count = 0
        last_exception = None

        while retry_count <= max_retries:
            start_time = time.time()
            try:
                async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
                    response = await client.get(url, headers=headers)
                    latency = time.time() - start_time

                    if response.status_code == 200:
                        return FetchResult(
                            content=response.text,
                            status_code=200,
                            latency_seconds=latency,
                            headers=dict(response.headers)
                        )

                    elif response.status_code == 429:
                        # Parse Retry-After header if present
                        retry_after_hdr = response.headers.get("Retry-After")
                        retry_after_seconds = None
                        if retry_after_hdr:
                            try:
                                retry_after_seconds = float(retry_after_hdr)
                            except ValueError:
                                retry_after_seconds = backoff_base_seconds * (2 ** retry_count)
                        else:
                            retry_after_seconds = backoff_base_seconds * (2 ** retry_count)

                        logger.warning(f"HTTP 429 Rate Limited on {url}. Retry-After: {retry_after_seconds}s")
                        
                        if retry_count < max_retries:
                            await asyncio.sleep(retry_after_seconds)
                            retry_count += 1
                            continue
                        else:
                            raise RateLimitException(
                                f"Rate limit exceeded (HTTP 429). Retries exhausted ({max_retries}).",
                                retry_after=retry_after_seconds,
                                status_code=429
                            )

                    elif response.status_code in (500, 502, 503, 504):
                        logger.warning(f"HTTP {response.status_code} server error on {url}. Retry {retry_count}/{max_retries}")
                        if retry_count < max_retries:
                            sleep_duration = backoff_base_seconds * (2 ** retry_count)
                            await asyncio.sleep(sleep_duration)
                            retry_count += 1
                            continue
                        else:
                            return FetchResult(
                                content=response.text,
                                status_code=response.status_code,
                                latency_seconds=latency,
                                headers=dict(response.headers)
                            )
                    else:
                        # Other non-200 status codes (e.g. 404, 403)
                        return FetchResult(
                            content=response.text,
                            status_code=response.status_code,
                            latency_seconds=latency,
                            headers=dict(response.headers)
                        )

            except (httpx.TimeoutException, httpx.NetworkError, httpx.ProtocolError) as e:
                latency = time.time() - start_time
                last_exception = e
                logger.warning(f"Network error on {url}: {e}. Retry {retry_count}/{max_retries}")
                if retry_count < max_retries:
                    sleep_duration = backoff_base_seconds * (2 ** retry_count)
                    await asyncio.sleep(sleep_duration)
                    retry_count += 1
                    continue
                else:
                    raise IOError(f"Network request failed for {url} after {max_retries} retries: {e}")

        raise IOError(f"Request failed for {url}: {last_exception}")

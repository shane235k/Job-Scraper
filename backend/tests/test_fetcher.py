import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from app.engine.fetcher import HttpFetcher, RateLimitException

@pytest.mark.asyncio
async def test_fetcher_200_ok():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Job Content</body></html>"
    mock_response.headers = {"Content-Type": "text/html"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        res = await HttpFetcher.fetch(
            url="https://test.source/jobs",
            source_id="test_src",
            min_interval_seconds=0.01,
            max_retries=1
        )
        assert res.status_code == 200
        assert "Job Content" in res.content

@pytest.mark.asyncio
async def test_fetcher_429_rate_limit():
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "1"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        with pytest.raises(RateLimitException) as exc_info:
            await HttpFetcher.fetch(
                url="https://test.source/jobs",
                source_id="test_src_429",
                min_interval_seconds=0.01,
                max_retries=1,
                backoff_base_seconds=0.01
            )
        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 1.0

@pytest.mark.asyncio
async def test_fetcher_500_server_error_retry():
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.headers = {}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        res = await HttpFetcher.fetch(
            url="https://test.source/jobs",
            source_id="test_src_500",
            min_interval_seconds=0.01,
            max_retries=2,
            backoff_base_seconds=0.01
        )
        assert res.status_code == 500
        assert mock_get.call_count == 3  # 1 initial + 2 retries

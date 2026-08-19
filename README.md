# Real Job Listing Ingestion & Resilience System

A production-grade, source-independent job ingestion system that repeatedly acquires real job listings from public sources (**Python Software Foundation Job Board** & **LinkedIn Public Guest Search** via real BeautifulSoup HTML scraping, plus **The Muse API** as a secondary adapter), normalizes & deduplicates listings into **PostgreSQL**, handles rate limits and transient errors Auditably, and exposes live system state through a **Vercel-inspired monochrome developer dashboard**.

---

## 1. Assignment Interpretation & Core Philosophy

The central goal of this project is to build an ingestion system that survives source failures, rate limits, and structural changes while maintaining **100% Data Integrity**:

- **REAL LIVE DATA ONLY**: Zero mock jobs, zero simulated data switches, zero fake metrics in production.
- **ACTUAL HTML SCRAPING**: Primary live sources extract real HTML from `https://www.python.org/jobs/` and `LinkedIn Public Guest Search` (`https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search`) using `httpx` + `BeautifulSoup4` + CSS selectors.
- **RESPONSIBLE CITIZENSHIP**: Request pacing, bounded exponential backoff, respecting `Retry-After` headers, and stopping when blocked rather than attempting anti-bot circumvention.
- **TRANSPARENT OBSERVABILITY**: Errors (HTTP 429, 503, Parser Failures) are displayed honestly on the UI and persisted in PostgreSQL without wiping historical records.

---

## 2. Source Selection & HTML Selectors

### 1. Primary Live Source: Python Software Foundation Job Board (`python_org`)
- **URL**: `https://www.python.org/jobs/`
- **Scraping Engine**: `httpx` + `BeautifulSoup4`
- **Target Container**: `ol.list-recent-jobs > li`
- **Extracted Fields**: `title`, `company`, `location`, `employment_type`, `posted_at`, `job_url`, `source_job_id`.

### 2. LinkedIn Public Guest Scraper (`linkedin`)
- **URL**: `https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search`
- **Scraping Engine**: `httpx` + `BeautifulSoup4`
- **Target Container**: `li > div.base-search-card`
- **Extracted Fields**: `title` (`h3.base-search-card__title`), `company` (`h4.base-search-card__subtitle`), `location` (`span.job-search-card__location`), `job_url` (`a.base-card__full-link`).

### 3. Secondary Source: The Muse (`muse`)
- **URL**: `https://www.themuse.com/api/public/jobs`
- **Type**: Real JSON API ingestion adapter demonstrating source independence.

---

## 3. Architecture

```text
               +-------------------------------------------------+
               |              REAL JOB SOURCES                   |
               | (python.org / LinkedIn Guest / The Muse API)    |
               +-----------------------+-------------------------+
                                       |
                                       | HTTP GET (httpx)
                                       v
               +-------------------------------------------------+
               |                HttpFetcher                      |
               |     (Pacing, Timeout, Backoff, 429)             |
               +-----------------------+-------------------------+
                                       |
                                       v
               +-------------------------------------------------+
               |            Source Adapter & Parser              |
               |       (BeautifulSoup4 / JSON Validator)         |
               +-----------------------+-------------------------+
                                       |
                                       v
               +-------------------------------------------------+
               |           Normalizer & Hasher                   |
               |       (Text Cleanup & SHA-256 Hash)             |
               +-----------------------+-------------------------+
                                       |
                                       v
               +-------------------------------------------------+
               |                 Deduplicator                    |
               |       ((source, source_job_id) / hash)          |
               +-----------------------+-------------------------+
                                       |
                                       v
               +-------------------------------------------------+
               |                 PostgreSQL                      |
               |       (jobs, sources, runs, errors)             |
               +-----------------------+-------------------------+
                                       |
               +-----------------------+-------------------------+
               |                    FastAPI                      |
               |        (REST Endpoints & Background)            |
               +-----------------------+-------------------------+
                                       |
                                       v
               +-------------------------------------------------+
               |           Vercel Monochrome UI                  |
               |             (React + CSS)                       |
               +-------------------------------------------------+
```

---

## 4. PostgreSQL Database Schema

The database consists of 4 relational tables:

1. **`jobs`**: Stores normalized job listings.
   - `id` (UUID PK), `source`, `source_job_id`, `title`, `company`, `location`, `description`, `job_url`, `posted_at`, `employment_type`, `remote_type`, `first_seen_at`, `last_seen_at`, `content_hash`, `created_at`, `updated_at`.
2. **`sources`**: Tracks health & ingestion status per source.
   - `id` PK, `name`, `source_type` (`html`/`api`), `url`, `is_enabled`, `health_status` (`HEALTHY`, `DEGRADED`, `UNAVAILABLE`), `last_successful_ingestion`, `last_attempted_ingestion`, `consecutive_failures`, `last_http_status`, `last_error`.
3. **`ingestion_runs`**: Persists run execution metrics.
   - `id` (UUID PK), `source_id`, `start_time`, `end_time`, `status` (`SUCCESS`, `PARTIAL`, `FAILED`), `jobs_fetched`, `jobs_created`, `jobs_updated`, `duplicates`, `http_failures`, `parser_failures`, `retry_count`, `error_summary`.
4. **`ingestion_errors`**: Detailed failure logs.
   - `id` (UUID PK), `run_id`, `source_id`, `error_type` (`HTTP_429`, `HTTP_5XX`, `PARSER_FAILURE`, `NETWORK_ERROR`), `http_status`, `message`, `details`, `timestamp`.

---

## 5. Local Setup & Execution

### Step 1: Configure Environment
```bash
cp .env.example .env
```

### Step 2: Run Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Step 3: Run Automated Pytest Suite
```bash
cd backend
python -m pytest -v
```

### Step 4: Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000`.

---

## 6. Docker Deployment

Launch the complete production stack (PostgreSQL + FastAPI Backend + React Frontend):

```bash
docker-compose up --build -d
```

- **Frontend UI**: `http://localhost:3000`
- **Backend REST API**: `http://localhost:8000/docs`

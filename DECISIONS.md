# Engineering Decisions & Detection Surface Analysis

This document provides a concise engineering overview answering the 3 core decision questions, followed by the Detection Surface & Mitigations analysis.

---

## 1. Core Engineering Decisions

### 1. Why this ingestion strategy over the obvious alternative you rejected?
We chose a **Decoupled Source-Adapter Architecture** (`BaseSourceAdapter`) using direct HTTP DOM scraping (`httpx` + `BeautifulSoup4`) with per-source request pacing (`asyncio.Lock`), dynamic Indian location & keyword rotation, exponential backoff, SHA-256 deduplication, and PostgreSQL persistence.

* **Alternative Rejected**: Headless browser automation (Playwright/Selenium) or third-party paid scraping API proxies (ScraperAPI, PhantomBuster).
* **Why Rejected**: Headless browsers are memory-heavy, slow ($10\text{s}$–$15\text{s}$ per page), and leak telltale bot signals (`navigator.webdriver = true`, canvas rendering anomalies). Paid scraping APIs hide the underlying engineering mechanics. Direct HTTP DOM scraping provides an authentic, high-performance, transparent engineering demonstration.

---

### 2. One trade-off you made under the time limit, and what you'd do with a real week.
* **Trade-off Made**: I would implemented a lightweight, non-blocking `asyncio` background scheduler with in-memory pacing locks rather than deploying distributed message queues (Celery + Redis) or residential proxy rotation networks.
* **What I'd Do With a Real Week**:
  1. **Distributed Queue Architecture**: Deploy Celery worker nodes backed by Redis for multi-tenant queue management and distributed rate-limiting.
  2. **Proxy Pool & TLS Fingerprint Rotation**: Integrate rotating residential IP proxy pools and TLS cipher spoofing (`curl_cffi`) to simulate diverse browser TLS handshakes.
  3. **Heuristic/LLM Fallback Parsing**: Implement a fallback parser using structural heuristics to extract job cards automatically when DOM class names change overnight.

---

### 3. Where did you use AI tools, and what did you personally verify or change afterward?
* **AI Tool Usage**: AI tools were used for writing initial boilerplate scaffolding (FastAPI & React), generating CSS styling tokens, and drafting unit test mocks.
* **What Was Personally Verified & Changed**:
  - Personally inspected and verified all real live HTTP responses, HTML DOM selectors (`ul.jobs-search__results-list > li`, `ol.list-recent-jobs > li`), and BeautifulSoup extraction paths on real web traffic.
  - Made sure that the architectue not only extracts from muse APIs or guest linkedin api but also actual linkedin job page, while ensuring that multiple layers exist to simulate human behavior.
  - Verified database records in PostgreSQL and deployment across Render and Vercel.
  - Modified the rotation engine so that now it not only rotates between keywords but also rotates between Indian locations, ensuring that we are not only scraping the same location again and again.
  - Offsets for job searching were added to make sure that the engine does not scrapes the same pages again and again.
---

## 2. Detection Surface & Mitigations

Protected job platforms (LinkedIn, Indeed, Naukri, Wellfound) evaluate automated traffic across multiple technical layers:

### A. Network & Protocol Layer
- **HTTP Header Order & User-Agent**: Default HTTP clients (e.g. `python-requests/2.x`) use fixed, non-browser header orders that trigger instant WAF blocks.
  - *Mitigation*: Our `HttpFetcher` ([fetcher.py](file:///c:/nvm/COLLEGE/INTSH/Acydon/backend/app/engine/fetcher.py)) injects full modern Chrome browser headers (`User-Agent`, `Accept-Language`, `Sec-CH-UA`).
- **TLS Fingerprinting**: Headless scripts present distinct TLS cipher suites differing from real browser handshakes.
  - *Mitigation*: We utilize `httpx.AsyncClient` with HTTP/1.1 & HTTP/2 connection pooling.

### B. Behavioral & Timing Layer
- **Burst Traffic & Uniform Spacing**: Sending 50 requests in 2 seconds or uniform 1.000s intervals signals automated scripts.
  - *Mitigation*: Implemented source pacing locks (`asyncio.Lock`) enforcing minimum intervals (`3.0s` delay for LinkedIn, `1.5s` for Python.org) with randomized timing jitter.
  - *Manual Cooldown Lock*: 45-second manual trigger cooldown lock prevents rapid-click spamming.

### C. Ingestion Strategy & Fallback (Plan B)
- **Source Independence**: `BaseSourceAdapter` decouples acquisition from sources.
- **Plan B Fallback Route**: When a primary source hits 3 consecutive failures (`UNAVAILABLE` status), the scheduler automatically routes tasks to secondary authorized adapters (`python_org` $\rightarrow$ `muse`).

---

## 3. Resilience & Where We Stop

### A. Overnight DOM Markup Changes
- **Parser Validation Failure**: Adapters enforce structural validation. If HTML markup changes, the parser raises `ValueError("PARSER VALIDATION FAILURE")`.
- **Data Preservation Guarantee**: The runner catches parser/network errors, logs an `IngestionError` row in PostgreSQL, and **preserves all existing PostgreSQL records**.

### B. Ethical Technical Boundaries We Do NOT Cross
1. **NO CAPTCHA Bypass**: We do not use automated CAPTCHA solving farms.
2. **NO Authentication Wall Bypassing**: We do not scrape private user accounts or authenticated sessions.
3. **NO IP Ban Evasion Escalation**: If blocked, the system halts execution, marks the source `UNAVAILABLE`, and triggers fallback routes.

$$\text{Detect} \longrightarrow \text{Backoff} \longrightarrow \text{Bounded Retry} \longrightarrow \text{Stop} \longrightarrow \text{Authorized Fallback}$$

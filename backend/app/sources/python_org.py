import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from app.sources.base import BaseSourceAdapter

class PythonOrgAdapter(BaseSourceAdapter):
    @property
    def source_id(self) -> str:
        return "python_org"

    @property
    def source_name(self) -> str:
        return "Python.org Jobs (HTML Scraper)"

    @property
    def source_type(self) -> str:
        return "html"

    @property
    def base_url(self) -> str:
        return "https://www.python.org/jobs/"

    def get_page_url(self, page_num: int) -> str:
        if page_num <= 1:
            return "https://www.python.org/jobs/"
        return f"https://www.python.org/jobs/?page={page_num}"

    def parse_page(self, content: str, url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(content, "html.parser")
        
        # Check for container element
        container = soup.select_one("ol.list-recent-jobs")
        if not container and "jobs" in url:
            # Check if there is an explicit empty state or if markup changed completely
            raise ValueError("PARSER VALIDATION FAILURE: Expected container 'ol.list-recent-jobs' was not found in HTML markup.")

        job_elements = soup.select("ol.list-recent-jobs > li")
        
        # On page 1, if container exists but has 0 items, raise parser error
        if page_num_is_1 := ("?page=" not in url or "?page=1" in url):
            if len(job_elements) == 0:
                raise ValueError("PARSER VALIDATION FAILURE: 'ol.list-recent-jobs' container was empty on page 1.")

        results = []
        for idx, item in enumerate(job_elements):
            title_elem = item.select_one("span.listing-company-name > a")
            if not title_elem:
                continue

            title = title_elem.text.strip()
            href = title_elem.get("href", "")
            job_url = f"https://www.python.org{href}" if href.startswith("/") else href

            # Extract source_job_id from URL path e.g. /jobs/8126/
            id_match = re.search(r"/jobs/(\d+)/", job_url)
            source_job_id = id_match.group(1) if id_match else f"py-{idx}"

            # Company name extraction
            company_elem = item.select_one("span.listing-company-name")
            company = "Unknown"
            if company_elem:
                company_text = company_elem.text.replace(title, "").strip()
                company = re.sub(r"\s+", " ", company_text).lstrip("New ").strip() or "Unknown"

            # Location
            loc_elem = item.select_one("span.listing-location")
            location = loc_elem.text.strip() if loc_elem else "Remote / Unspecified"

            # Employment / Category type
            type_elem = item.select_one("span.listing-job-type")
            employment_type = type_elem.text.strip() if type_elem else None

            # Posted date
            time_elem = item.select_one("time")
            posted_at_raw = time_elem.get("datetime") if time_elem else None

            results.append({
                "source_job_id": source_job_id,
                "title": title,
                "company": company,
                "location": location,
                "description": f"Position: {title} at {company}. Category: {employment_type or 'General'}. Location: {location}.",
                "job_url": job_url,
                "posted_at": posted_at_raw,
                "employment_type": employment_type,
                "remote_type": "Remote" if "remote" in location.lower() or (employment_type and "remote" in employment_type.lower()) else "Onsite/Hybrid"
            })

        return results

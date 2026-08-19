import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from app.sources.base import BaseSourceAdapter

class LinkedInGuestAdapter(BaseSourceAdapter):
    """
    Adapter for LinkedIn Direct Public Search Page (`https://www.linkedin.com/jobs/search`).
    Scrapes raw full-page HTML without requiring user login or account authentication.
    """
    @property
    def source_id(self) -> str:
        return "linkedin"

    @property
    def source_name(self) -> str:
        return "LinkedIn Jobs (Direct HTML Scraper)"

    @property
    def source_type(self) -> str:
        return "html"

    @property
    def base_url(self) -> str:
        return "https://www.linkedin.com/jobs/search"

    def get_page_url(self, page_num: int) -> str:
        start_offset = (page_num - 1) * 25
        return f"https://www.linkedin.com/jobs/search?keywords=python&location=United+States&start={start_offset}"

    def parse_page(self, content: str, url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(content, "html.parser")
        
        cards = soup.select("ul.jobs-search__results-list > li") or soup.select("li")
        if not cards and "start=0" in url:
            raise ValueError("PARSER VALIDATION FAILURE: No job listing elements found in LinkedIn search page DOM.")

        results = []
        for idx, card in enumerate(cards):
            title_elem = card.select_one("h3.base-search-card__title") or card.select_one("h3")
            company_elem = card.select_one("h4.base-search-card__subtitle") or card.select_one("h4")
            loc_elem = card.select_one("span.job-search-card__location")
            link_elem = card.select_one("a.base-card__full-link") or card.select_one("a")
            time_elem = card.select_one("time")

            if not title_elem or not company_elem:
                continue

            title = title_elem.text.strip()
            company = company_elem.text.strip()
            location = loc_elem.text.strip() if loc_elem else "Remote / Unspecified"
            
            raw_url = link_elem["href"] if link_elem and link_elem.has_attr("href") else ""
            job_url = raw_url.split("?")[0] if raw_url else ""

            id_match = re.search(r"-(\d{8,12})$", job_url) or re.search(r"/view/.*?(\d+)", raw_url)
            source_job_id = id_match.group(1) if id_match else f"li-{idx}"

            posted_at = time_elem.get("datetime") if time_elem and time_elem.has_attr("datetime") else None

            results.append({
                "source_job_id": source_job_id,
                "title": title,
                "company": company,
                "location": location,
                "description": f"Position: {title} at {company}. Location: {location}. Source: LinkedIn Direct Page Search.",
                "job_url": job_url,
                "posted_at": posted_at,
                "employment_type": "Full-time",
                "remote_type": "Remote" if "remote" in location.lower() else "Onsite/Hybrid"
            })

        return results

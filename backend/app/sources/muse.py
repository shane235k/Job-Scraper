import json
from typing import List, Dict, Any
from app.sources.base import BaseSourceAdapter

class MuseAdapter(BaseSourceAdapter):
    @property
    def source_id(self) -> str:
        return "muse"

    @property
    def source_name(self) -> str:
        return "The Muse (Public API)"

    @property
    def source_type(self) -> str:
        return "api"

    @property
    def base_url(self) -> str:
        return "https://www.themuse.com/api/public/jobs"

    def get_page_url(self, page_num: int) -> str:
        return f"https://www.themuse.com/api/public/jobs?page={page_num}"

    def parse_page(self, content: str, url: str) -> List[Dict[str, Any]]:
        try:
            data = json.loads(content)
        except Exception as e:
            raise ValueError(f"PARSER VALIDATION FAILURE: Could not parse response as JSON. Details: {e}")

        if not isinstance(data, dict) or "results" not in data or not isinstance(data["results"], list):
            raise ValueError("PARSER VALIDATION FAILURE: Expected array key 'results' was missing from API response.")

        results = []
        for item in data["results"]:
            source_job_id = str(item.get("id")) if item.get("id") is not None else None
            title = item.get("name", "Untitled")

            company_data = item.get("company", {})
            company = company_data.get("name", "Unknown") if isinstance(company_data, dict) else "Unknown"

            locations_data = item.get("locations", [])
            location = locations_data[0].get("name", "Unspecified") if locations_data and isinstance(locations_data[0], dict) else "Unspecified"

            refs_data = item.get("refs", {})
            job_url = refs_data.get("landing_page") if isinstance(refs_data, dict) else f"https://www.themuse.com/jobs/{source_job_id}"

            description = item.get("contents", "")
            posted_at = item.get("publication_date")

            levels = item.get("levels", [])
            employment_type = levels[0].get("name") if levels and isinstance(levels[0], dict) else None

            results.append({
                "source_job_id": source_job_id,
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "job_url": job_url,
                "posted_at": posted_at,
                "employment_type": employment_type,
                "remote_type": "Remote" if "remote" in location.lower() else None
            })

        return results

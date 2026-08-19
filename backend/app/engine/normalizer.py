import re
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from dateutil import parser as date_parser

class DataNormalizer:
    """
    Normalizes job fields into standard types & creates deterministic content hash.
    """
    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        # Remove HTML tags if any residual tags remain
        clean = re.sub(r"<[^>]+>", " ", text)
        # Collapse multiple spaces
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean if clean else None

    @staticmethod
    def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        if not dt_str:
            return None
        try:
            return date_parser.parse(dt_str)
        except Exception:
            return None

    @classmethod
    def normalize_job(cls, raw: Dict[str, Any], source_id: str) -> Dict[str, Any]:
        title = cls.clean_text(raw.get("title")) or "Untitled Position"
        company = cls.clean_text(raw.get("company")) or "Unknown Company"
        location = cls.clean_text(raw.get("location")) or "Unspecified Location"
        description = cls.clean_text(raw.get("description"))
        job_url = cls.clean_text(raw.get("job_url"))
        source_job_id = cls.clean_text(raw.get("source_job_id"))
        
        posted_at_raw = raw.get("posted_at")
        posted_at = cls.parse_datetime(str(posted_at_raw)) if posted_at_raw else None

        employment_type = cls.clean_text(raw.get("employment_type"))
        remote_type = cls.clean_text(raw.get("remote_type"))

        # Generate SHA-256 content hash
        hash_input = f"{title.lower()}|{company.lower()}|{location.lower()}|{(job_url or '').lower()}"
        content_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        return {
            "source": source_id,
            "source_job_id": source_job_id,
            "title": title,
            "company": company,
            "location": location,
            "description": description,
            "job_url": job_url,
            "posted_at": posted_at,
            "employment_type": employment_type,
            "remote_type": remote_type,
            "content_hash": content_hash
        }

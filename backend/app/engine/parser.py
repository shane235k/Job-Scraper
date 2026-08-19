from typing import List, Dict, Any
from app.sources.base import BaseSourceAdapter

class PayloadParser:
    """
    Parser wrapper enforcing schema validation rules.
    If the DOM structure changed or required keys are missing, raises ValueError.
    """
    @staticmethod
    def parse_and_validate(adapter: BaseSourceAdapter, content: str, url: str) -> List[Dict[str, Any]]:
        raw_records = adapter.parse_page(content, url)
        
        # Validate extracted records
        for idx, rec in enumerate(raw_records):
            if not isinstance(rec, dict):
                raise ValueError(f"PARSER VALIDATION FAILURE: Extracted item at index {idx} is not a dictionary.")
            if "title" not in rec or not rec["title"]:
                raise ValueError(f"PARSER VALIDATION FAILURE: Required field 'title' missing or empty at item {idx}.")
        
        return raw_records

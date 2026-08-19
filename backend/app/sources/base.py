from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class BaseSourceAdapter(ABC):
    """
    Abstract base class for all job sources.
    Source adapters define source-specific URLs, pagination, and parsing logic,
    leaving acquisition control (pacing, retries, backoff) to the engine fetcher.
    """
    
    @property
    @abstractmethod
    def source_id(self) -> str:
        """Unique key for the source (e.g. 'python_org', 'muse')."""
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human readable name."""
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        """'html' or 'api'."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Primary target URL."""
        pass

    @abstractmethod
    def get_page_url(self, page_num: int) -> str:
        """Construct page URL for page N (1-indexed)."""
        pass

    @abstractmethod
    def parse_page(self, content: str, url: str) -> List[Dict[str, Any]]:
        """
        Parse raw HTML or JSON content and return a list of raw job dicts.
        Must raise ValueError if expected structure is missing (Parser Validation Failure).
        """
        pass

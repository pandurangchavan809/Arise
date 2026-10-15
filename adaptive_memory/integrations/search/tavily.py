"""
Tavily Search Provider implementation.
Performs real-time web retrieval using the Tavily Search API.
"""

from __future__ import annotations

from typing import List, Optional
import httpx
import structlog

from adaptive_memory.config import get_settings
from adaptive_memory.integrations.search.base import SearchProvider, SearchResult

logger = structlog.get_logger(__name__)


class TavilyProvider(SearchProvider):
    """
    Search provider implementation backed by Tavily API.
    """
    TAVILY_ENDPOINT = "https://api.tavily.com/search"

    def __init__(self, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.tavily_api_key

    def is_available(self) -> bool:
        """Check if Tavily API key is available."""
        return bool(self.api_key)

    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Query Tavily search endpoint and normalize results."""
        if not self.is_available():
            logger.warning("Tavily search invoked but TAVILY_API_KEY is not configured")
            return []

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_raw_content": False,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.TAVILY_ENDPOINT, json=payload)
                response.raise_for_status()
                data = response.json()

            results: List[SearchResult] = []
            for item in data.get("results", []):
                results.append(
                    SearchResult(
                        title=item.get("title", "Untitled"),
                        url=item.get("url", ""),
                        content=item.get("content", ""),
                        score=item.get("score"),
                        raw=item,
                    )
                )
            return results
        except httpx.HTTPError as e:
            logger.error("Tavily search API request failed", query=query, error=str(e))
            return []
        except Exception as e:
            logger.error("Unexpected error during Tavily search", query=query, error=str(e))
            return []

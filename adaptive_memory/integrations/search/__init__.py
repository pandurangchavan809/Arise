"""
Search integration package.
Exposes SearchProvider, SearchResult, and TavilyProvider.
"""

from adaptive_memory.integrations.search.base import SearchProvider, SearchResult
from adaptive_memory.integrations.search.tavily import TavilyProvider

__all__ = ["SearchProvider", "SearchResult", "TavilyProvider"]

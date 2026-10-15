"""
Abstract Search Provider interface for Adaptive Memory Runtime.
Provides contracts for external real-time web retrieval.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Normalized search result model."""
    title: str = Field(..., description="Document or page title")
    url: str = Field(..., description="Source link URL")
    content: str = Field(..., description="Extracted snippet or page content")
    score: Optional[float] = Field(default=None, description="Relevance rank score")
    raw: Optional[Dict[str, Any]] = Field(default=None, description="Raw provider payload")


class SearchProvider(ABC):
    """
    Abstract interface for search providers.
    """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if search provider credentials and service are configured."""
        pass

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Execute real-time web or external document search.
        """
        pass

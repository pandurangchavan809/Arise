"""
Abstract storage backend interface for Adaptive Memory Runtime.
Defines contracts for persistence, full-text retrieval, updates, and lifecycle queries.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from adaptive_memory.models import MemoryRecord, MemoryType


class StorageBackend(ABC):
    """
    Abstract pluggable storage interface for memory persistence and retrieval.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize database schemas, tables, and indices."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Gracefully release connection pools and database resources."""
        pass

    @abstractmethod
    async def store(self, record: MemoryRecord) -> MemoryRecord:
        """Persist a new memory record."""
        pass

    @abstractmethod
    async def get(self, memory_id: str) -> Optional[MemoryRecord]:
        """Fetch a specific memory record by ID."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        user_id: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryRecord]:
        """
        Execute full-text and filtered search for candidate memories.
        """
        pass

    @abstractmethod
    async def update(self, memory_id: str, updates: Dict[str, Any]) -> MemoryRecord:
        """
        Update specific fields of an existing memory record.
        """
        pass

    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """
        Remove a memory record by ID.
        """
        pass

    @abstractmethod
    async def list_by_type(
        self,
        user_id: str,
        memory_type: MemoryType,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MemoryRecord]:
        """
        List memories filtered by user and memory type with pagination.
        """
        pass

    @abstractmethod
    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Aggregate storage metrics and memory counts for a user.
        """
        pass

    @abstractmethod
    async def get_expired(self, before: datetime) -> List[MemoryRecord]:
        """
        Retrieve all active memories with an expiration timestamp prior to `before`.
        """
        pass

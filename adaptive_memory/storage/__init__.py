"""
Storage package for Adaptive Memory Runtime.
Exposes StorageBackend abstract interface and SQLiteStorage implementation.
"""

from adaptive_memory.storage.interface import StorageBackend
from adaptive_memory.storage.sqlite import SQLiteStorage

__all__ = [
    "StorageBackend",
    "SQLiteStorage",
]

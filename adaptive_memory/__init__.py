"""
Adaptive Memory Runtime: Production-Grade Memory Middleware for AI Agents.
Provides deterministic, explainable memory quality management, conflict resolution,
and edge budget enforcement.
"""

__version__ = "0.1.0"

from adaptive_memory.config import Settings, get_settings
from adaptive_memory.core.budget import EdgeBudgetController
from adaptive_memory.core.conflicts import ConflictDetector, ConflictGroup
from adaptive_memory.core.lifecycle import MemoryLifecycle
from adaptive_memory.core.manager import MemoryQualityManager
from adaptive_memory.core.quality import QualityScorer
from adaptive_memory.core.ranking import MemoryRanker
from adaptive_memory.models import (
    DecisionType,
    EdgeBudget,
    MemoryCandidate,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    OutcomeType,
    QualityDecision,
    QualityScore,
    RecallResult,
    SafetyTier,
)
from adaptive_memory.storage.interface import StorageBackend
from adaptive_memory.storage.sqlite import SQLiteStorage

__all__ = [
    "__version__",
    "Settings",
    "get_settings",
    "MemoryRecord",
    "MemoryType",
    "MemoryStatus",
    "SafetyTier",
    "OutcomeType",
    "DecisionType",
    "QualityScore",
    "QualityDecision",
    "MemoryCandidate",
    "RecallResult",
    "EdgeBudget",
    "MemoryQualityManager",
    "QualityScorer",
    "MemoryRanker",
    "EdgeBudgetController",
    "ConflictDetector",
    "ConflictGroup",
    "MemoryLifecycle",
    "StorageBackend",
    "SQLiteStorage",
]

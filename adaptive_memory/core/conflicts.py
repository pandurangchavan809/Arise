"""
Conflict detection and resolution subsystem for memory candidates.
Identifies mutually inconsistent memories and resolves them using deterministic precedence rules:
newer > older, explicit > implicit, and higher confidence wins.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
import structlog

from adaptive_memory.models import MemoryRecord, SafetyTier

logger = structlog.get_logger(__name__)

STOP_WORDS: Set[str] = {
    "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or", "is", "are", "was",
    "were", "i", "my", "you", "your", "he", "she", "it", "they", "we"
}


class ConflictGroup(BaseModel):
    """Represents a set of conflicting memories with diagnostic details."""
    memory_ids: List[str]
    conflict_type: str = Field(..., description="e.g., 'fact_superseded', 'direct_contradiction', 'preference_update'")
    resolution_id: Optional[str] = Field(default=None, description="Memory ID chosen as winner")
    reason: Optional[str] = Field(default=None, description="Explanation of resolution winner")


class ConflictDetector:
    """
    Detects semantic or factual conflicts among candidate memories for a user.
    """

    def __init__(self, keyword_overlap_threshold: float = 0.6) -> None:
        self.overlap_threshold = keyword_overlap_threshold

    @staticmethod
    def _keywords(text: str) -> Set[str]:
        words = re.findall(r"\b\w{3,}\b", text.lower())
        return {w for w in words if w not in STOP_WORDS}

    def detect(self, candidates: List[MemoryRecord]) -> List[ConflictGroup]:
        """
        Scan candidates for pairwise or cluster conflicts.
        Flag pairs that share dominant subject keywords but have distinct, incompatible statements.
        """
        conflicts: List[ConflictGroup] = []
        visited_pairs: Set[tuple] = set()

        for i, mem_a in enumerate(candidates):
            words_a = self._keywords(mem_a.content)
            if not words_a:
                continue

            for j, mem_b in enumerate(candidates):
                if i >= j or mem_a.user_id != mem_b.user_id:
                    continue

                pair_key = (min(mem_a.id, mem_b.id), max(mem_a.id, mem_b.id))
                if pair_key in visited_pairs:
                    continue

                words_b = self._keywords(mem_b.content)
                if not words_b:
                    continue

                overlap = words_a.intersection(words_b)
                overlap_ratio = len(overlap) / max(min(len(words_a), len(words_b)), 1)

                # Explicit metadata match or high topic overlap with different content
                explicit_conflict = (
                    mem_a.metadata.get("conflicts_with") == mem_b.id
                    or mem_b.metadata.get("conflicts_with") == mem_a.id
                    or (mem_a.task_context and mem_a.task_context == mem_b.task_context and mem_a.content != mem_b.content)
                )

                if (overlap_ratio >= self.overlap_threshold and mem_a.content != mem_b.content) or explicit_conflict:
                    visited_pairs.add(pair_key)
                    c_type = "explicit_link" if explicit_conflict else "keyword_overlap_collision"
                    group = ConflictGroup(
                        memory_ids=[mem_a.id, mem_b.id],
                        conflict_type=c_type,
                    )
                    # Resolve immediately for the group
                    resolved_record, reason = self._resolve_pair(mem_a, mem_b)
                    group.resolution_id = resolved_record.id
                    group.reason = reason
                    conflicts.append(group)
                    logger.debug(
                        "Conflict detected",
                        mem_a=mem_a.id,
                        mem_b=mem_b.id,
                        conflict_type=c_type,
                        winner=resolved_record.id,
                        reason=reason
                    )

        return conflicts

    def _resolve_pair(self, mem_a: MemoryRecord, mem_b: MemoryRecord) -> tuple[MemoryRecord, str]:
        """
        Resolve conflict between two memories.
        Rules:
        1. Higher Safety Tier must be respected (T4 > T3 > T2 > T1 > T0).
        2. Explicit over implicit (source == 'user' vs 'agent' / 'tool').
        3. Higher confidence wins (if delta > 0.15).
        4. Newer updated_at wins.
        """
        # Safety tier rule: higher safety tier cannot be suppressed by lower
        if mem_a.risk_level.level > mem_b.risk_level.level:
            return mem_a, f"Safety tier {mem_a.risk_level.value} supersedes {mem_b.risk_level.value}"
        if mem_b.risk_level.level > mem_a.risk_level.level:
            return mem_b, f"Safety tier {mem_b.risk_level.value} supersedes {mem_a.risk_level.value}"

        # Explicit user origin wins over agent or tool deduction
        if mem_a.source == "user" and mem_b.source != "user":
            return mem_a, "Explicit user origin supersedes non-user source"
        if mem_b.source == "user" and mem_a.source != "user":
            return mem_b, "Explicit user origin supersedes non-user source"

        # Higher confidence wins if difference is noticeable
        conf_diff = mem_a.confidence - mem_b.confidence
        if conf_diff > 0.15:
            return mem_a, f"Confidence {mem_a.confidence:.2f} significantly exceeds {mem_b.confidence:.2f}"
        if conf_diff < -0.15:
            return mem_b, f"Confidence {mem_b.confidence:.2f} significantly exceeds {mem_a.confidence:.2f}"

        # Newer timestamp wins
        time_a = mem_a.updated_at or mem_a.created_at
        time_b = mem_b.updated_at or mem_b.created_at
        if time_a >= time_b:
            return mem_a, f"Newer memory ({time_a.isoformat()}) supersedes older ({time_b.isoformat()})"
        return mem_b, f"Newer memory ({time_b.isoformat()}) supersedes older ({time_a.isoformat()})"

    def resolve(self, conflict_group: ConflictGroup, candidates_by_id: Dict[str, MemoryRecord]) -> MemoryRecord:
        """
        Resolve a multi-candidate conflict group by tournament comparison.
        """
        active_candidates = [candidates_by_id[mid] for mid in conflict_group.memory_ids if mid in candidates_by_id]
        if not active_candidates:
            raise ValueError(f"No candidate records found for IDs in group {conflict_group.memory_ids}")

        current_winner = active_candidates[0]
        final_reason = "Default primary selection"

        for next_cand in active_candidates[1:]:
            current_winner, final_reason = self._resolve_pair(current_winner, next_cand)

        conflict_group.resolution_id = current_winner.id
        conflict_group.reason = final_reason
        return current_winner

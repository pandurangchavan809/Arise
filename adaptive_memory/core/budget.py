"""
Edge budget controller enforcing token limits, item count bounds, and efficiency constraints.
Ensures context windows remain concise and high-utility under edge environments.
"""

from __future__ import annotations

import math
from typing import List, Tuple
import structlog

from adaptive_memory.models import DecisionType, EdgeBudget, MemoryCandidate, QualityDecision, SafetyTier

logger = structlog.get_logger(__name__)


class EdgeBudgetController:
    """
    Enforces hardware, token, and memory count constraints on candidate memory injection.
    """

    def __init__(self, budget: EdgeBudget) -> None:
        self.budget = budget

    @staticmethod
    def estimate_tokens(content: str) -> int:
        """
        Estimate token count using the standard ~4 characters per token approximation.
        Ensures a minimum of 1 token for non-empty content.
        """
        if not content:
            return 0
        return max(1, math.ceil(len(content) / 4.0))

    def candidate_tokens(self, candidate: MemoryCandidate) -> int:
        """Estimate total tokens consumed by a memory candidate including metadata overhead."""
        base_tokens = self.estimate_tokens(candidate.memory.content)
        # Overhead for framing/timestamps/identifiers
        overhead = 8
        return base_tokens + overhead

    def within_budget(self, selected: List[MemoryCandidate]) -> bool:
        """Check if candidate list meets all edge budget limits."""
        if len(selected) > self.budget.max_memories:
            return False
        total_tokens = sum(self.candidate_tokens(c) for c in selected)
        return total_tokens <= self.budget.max_context_tokens

    def apply(self, candidates: List[MemoryCandidate]) -> Tuple[List[MemoryCandidate], List[MemoryCandidate]]:
        """
        Partition candidates into selected and suppressed based on budget limits and quality efficiency.
        Candidates MUST already be sorted in desired precedence order (e.g. by MemoryRanker).

        Preserves SafetyTier >= T2 records with higher priority over lower-tier records
        to fulfill the safety requirement: "A memory with risk_level >= T2 cannot be suppressed
        by a lower-tier memory".
        """
        selected: List[MemoryCandidate] = []
        suppressed: List[MemoryCandidate] = []
        used_tokens = 0

        # High-risk/critical tiers (>= T2) must be prioritized
        for cand in candidates:
            cand_tokens = self.candidate_tokens(cand)

            # Check if candidate has already been suppressed (e.g. by conflict detection or low score)
            if cand.decision.decision == DecisionType.SUPPRESSED:
                suppressed.append(cand)
                continue

            # Check count budget
            if len(selected) >= self.budget.max_memories:
                # If current candidate is T2 or higher and lowest selected is lower tier, can swap
                if cand.memory.risk_level >= SafetyTier.T2_OPERATIONAL:
                    swap_idx = None
                    for idx, sel in enumerate(reversed(selected)):
                        actual_idx = len(selected) - 1 - idx
                        if sel.memory.risk_level < SafetyTier.T2_OPERATIONAL:
                            swap_idx = actual_idx
                            break
                    if swap_idx is not None:
                        swapped = selected.pop(swap_idx)
                        used_tokens -= self.candidate_tokens(swapped)
                        swapped.decision = QualityDecision(
                            decision=DecisionType.SUPPRESSED,
                            reason=f"Evicted for higher safety-tier memory {cand.memory.id} ({cand.memory.risk_level.value})"
                        )
                        suppressed.append(swapped)
                        selected.append(cand)
                        used_tokens += cand_tokens
                        continue

                cand.decision = QualityDecision(
                    decision=DecisionType.SUPPRESSED,
                    reason=f"Exceeded max_memories budget limit of {self.budget.max_memories}"
                )
                suppressed.append(cand)
                continue

            # Check token budget
            if (used_tokens + cand_tokens) > self.budget.max_context_tokens:
                # If candidate is T2+ and lower tier memories can be evicted to make space
                if cand.memory.risk_level >= SafetyTier.T2_OPERATIONAL:
                    swap_idx = None
                    for idx, sel in enumerate(reversed(selected)):
                        actual_idx = len(selected) - 1 - idx
                        if sel.memory.risk_level < SafetyTier.T2_OPERATIONAL:
                            # Check if removing this lower-tier memory frees up enough space
                            if (used_tokens - self.candidate_tokens(sel) + cand_tokens) <= self.budget.max_context_tokens:
                                swap_idx = actual_idx
                                break
                    if swap_idx is not None:
                        swapped = selected.pop(swap_idx)
                        used_tokens -= self.candidate_tokens(swapped)
                        swapped.decision = QualityDecision(
                            decision=DecisionType.SUPPRESSED,
                            reason=f"Evicted for higher safety-tier memory {cand.memory.id} ({cand.memory.risk_level.value})"
                        )
                        suppressed.append(swapped)
                        selected.append(cand)
                        used_tokens += cand_tokens
                        continue

                cand.decision = QualityDecision(
                    decision=DecisionType.SUPPRESSED,
                    reason=f"Exceeded max_context_tokens limit ({used_tokens + cand_tokens} > {self.budget.max_context_tokens})"
                )
                suppressed.append(cand)
                continue

            # Within budget
            selected.append(cand)
            used_tokens += cand_tokens

        logger.debug(
            "Edge budget applied",
            selected_count=len(selected),
            suppressed_count=len(suppressed),
            total_tokens=used_tokens,
            max_tokens=self.budget.max_context_tokens,
        )
        return selected, suppressed

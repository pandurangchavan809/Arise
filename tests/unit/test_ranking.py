"""
Unit tests for MemoryRanker: quality ranking, budget constraints, context optimization, and edge cases.
"""

import pytest

from adaptive_memory.core.budget import EdgeBudgetController
from adaptive_memory.core.ranking import MemoryRanker
from adaptive_memory.models import (
    DecisionType,
    EdgeBudget,
    MemoryCandidate,
    MemoryRecord,
    MemoryType,
    QualityDecision,
    QualityScore,
    SafetyTier,
)


@pytest.fixture
def ranker() -> MemoryRanker:
    return MemoryRanker()


def _make_candidate(
    cid: str,
    content: str,
    total_score: float,
    risk_level: SafetyTier = SafetyTier.T0_CASUAL,
    decision_type: DecisionType = DecisionType.INCLUDED,
) -> MemoryCandidate:
    mem = MemoryRecord(
        id=cid,
        user_id="user_rank",
        content=content,
        memory_type=MemoryType.LONG_TERM,
        risk_level=risk_level,
    )
    score = QualityScore(
        relevance=total_score,
        utility=total_score,
        confidence=total_score,
        recency=total_score,
        conflict_risk=0.0,
        total=total_score,
    )
    decision = QualityDecision(decision=decision_type, reason="Initial candidate")
    return MemoryCandidate(memory=mem, score=score, decision=decision)


def test_empty_candidates(ranker: MemoryRanker):
    """Test ranking when candidates list is empty."""
    budget = EdgeBudget(max_memories=10, max_context_tokens=1000)
    selected, suppressed = ranker.rank([], budget)
    assert selected == []
    assert suppressed == []


def test_single_candidate(ranker: MemoryRanker):
    """Test ranking with a single valid candidate."""
    budget = EdgeBudget(max_memories=5, max_context_tokens=500)
    cand = _make_candidate("c1", "Single candidate memory", 0.75)
    selected, suppressed = ranker.rank([cand], budget)

    assert len(selected) == 1
    assert selected[0].memory.id == "c1"
    assert len(suppressed) == 0


def test_rank_by_quality(ranker: MemoryRanker):
    """Test candidates are ordered primarily by quality score descending."""
    budget = EdgeBudget(max_memories=5, max_context_tokens=2000)
    c_low = _make_candidate("c_low", "Low quality memory", 0.3)
    c_mid = _make_candidate("c_mid", "Medium quality memory", 0.6)
    c_high = _make_candidate("c_high", "High quality memory", 0.9)

    selected, _ = ranker.rank([c_low, c_mid, c_high], budget)

    assert [c.memory.id for c in selected] == ["c_high", "c_mid", "c_low"]


def test_budget_max_memories(ranker: MemoryRanker):
    """Test enforcing max_memories budget limit."""
    budget = EdgeBudget(max_memories=2, max_context_tokens=5000)
    c1 = _make_candidate("c1", "Memory 1", 0.9)
    c2 = _make_candidate("c2", "Memory 2", 0.8)
    c3 = _make_candidate("c3", "Memory 3", 0.7)
    c4 = _make_candidate("c4", "Memory 4", 0.6)

    selected, suppressed = ranker.rank([c1, c2, c3, c4], budget)

    assert len(selected) == 2
    assert [c.memory.id for c in selected] == ["c1", "c2"]
    assert len(suppressed) == 2
    assert all(c.decision.decision == DecisionType.SUPPRESSED for c in suppressed)


def test_budget_max_tokens(ranker: MemoryRanker):
    """Test suppressing candidates that exceed token budget ceiling."""
    # A candidate with 100 characters has ~25 tokens + 8 overhead = 33 tokens
    # Budget of 50 tokens allows only 1 candidate
    budget = EdgeBudget(max_memories=5, max_context_tokens=50)
    c1 = _make_candidate("c1", "First long memory with significant text " * 3, 0.9)
    c2 = _make_candidate("c2", "Second long memory with significant text " * 3, 0.8)

    selected, suppressed = ranker.rank([c1, c2], budget)

    assert len(selected) == 1
    assert selected[0].memory.id == "c1"
    assert len(suppressed) == 1
    assert "max_context_tokens" in suppressed[0].decision.reason


def test_prefer_smaller_context(ranker: MemoryRanker):
    """Test that between equal quality scores, shorter content is prioritized for economy."""
    budget = EdgeBudget(max_memories=5, max_context_tokens=1000)
    long_content = "Word " * 60  # Higher token footprint
    short_content = "Word " * 5   # Minimal token footprint

    c_long = _make_candidate("c_long", long_content, 0.8)
    c_short = _make_candidate("c_short", short_content, 0.8)

    selected, _ = ranker.rank([c_long, c_short], budget)

    # c_short should sort before c_long due to economy_factor
    assert selected[0].memory.id == "c_short"
    assert selected[1].memory.id == "c_long"

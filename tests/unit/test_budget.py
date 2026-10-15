"""
Unit tests for EdgeBudgetController: token estimation, capacity enforcement, and budget checks.
"""

import pytest

from adaptive_memory.config import Settings
from adaptive_memory.core.budget import EdgeBudgetController
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


def _make_candidate(content: str, score_val: float = 0.8, risk: SafetyTier = SafetyTier.T0_CASUAL) -> MemoryCandidate:
    mem = MemoryRecord(
        user_id="user_budget",
        content=content,
        memory_type=MemoryType.LONG_TERM,
        risk_level=risk,
    )
    score = QualityScore(total=score_val)
    decision = QualityDecision(decision=DecisionType.INCLUDED, reason="Candidate OK")
    return MemoryCandidate(memory=mem, score=score, decision=decision)


def test_token_estimation():
    """Test token estimation: ~4 chars per token, minimum 1 token for non-empty string."""
    assert EdgeBudgetController.estimate_tokens("") == 0
    assert EdgeBudgetController.estimate_tokens("a") == 1
    assert EdgeBudgetController.estimate_tokens("abcd") == 1
    assert EdgeBudgetController.estimate_tokens("abcde") == 2
    assert EdgeBudgetController.estimate_tokens("a" * 100) == 25


def test_default_budget():
    """Test building default EdgeBudget from Settings configuration."""
    settings = Settings(
        max_memories=15,
        max_context_tokens=1500,
        max_latency_ms=120,
        max_storage_bytes=52428800,
    )
    budget = settings.get_default_budget()

    assert budget.max_memories == 15
    assert budget.max_context_tokens == 1500
    assert budget.max_latency_ms == 120
    assert budget.max_storage_bytes == 52428800


def test_within_budget():
    """Test within_budget validation method accurately reports True or False."""
    budget = EdgeBudget(max_memories=2, max_context_tokens=100)
    controller = EdgeBudgetController(budget)

    # 1 candidate with ~25 tokens + 8 overhead = 33 tokens (<= 100)
    c1 = _make_candidate("x" * 100)
    assert controller.within_budget([c1]) is True

    # 2 candidates = ~66 tokens (<= 100) and count == 2 (<= 2)
    c2 = _make_candidate("x" * 100)
    assert controller.within_budget([c1, c2]) is True

    # 3 candidates exceeds max_memories (3 > 2)
    c3 = _make_candidate("x" * 100)
    assert controller.within_budget([c1, c2, c3]) is False


def test_exceeds_memory_budget():
    """Test EdgeBudgetController suppresses candidates beyond max_memories limit."""
    budget = EdgeBudget(max_memories=2, max_context_tokens=2000)
    controller = EdgeBudgetController(budget)

    c1 = _make_candidate("Item 1")
    c2 = _make_candidate("Item 2")
    c3 = _make_candidate("Item 3")

    selected, suppressed = controller.apply([c1, c2, c3])

    assert len(selected) == 2
    assert len(suppressed) == 1
    assert suppressed[0].decision.decision == DecisionType.SUPPRESSED
    assert "max_memories" in suppressed[0].decision.reason


def test_exceeds_token_budget():
    """Test EdgeBudgetController suppresses candidates exceeding max_context_tokens."""
    # Each 40-char candidate = 10 tokens + 8 overhead = 18 tokens
    # Budget of 30 tokens accommodates only 1 candidate (18 tokens), second would reach 36 tokens
    budget = EdgeBudget(max_memories=5, max_context_tokens=30)
    controller = EdgeBudgetController(budget)

    c1 = _make_candidate("A" * 40)
    c2 = _make_candidate("B" * 40)

    selected, suppressed = controller.apply([c1, c2])

    assert len(selected) == 1
    assert len(suppressed) == 1
    assert "max_context_tokens" in suppressed[0].decision.reason

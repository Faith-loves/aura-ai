from datetime import UTC, datetime, timedelta

from aura.memory.models import MemoryRecord, MemoryType
from aura.memory.scorer import MemoryScorer


def test_lexical_similarity_prefers_matching_memory():
    scorer = MemoryScorer()

    matching_memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="Python is a programming language.",
    )

    unrelated_memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="The weather is sunny today.",
    )

    matching_score = scorer.score(
        "Python programming",
        matching_memory,
    )

    unrelated_score = scorer.score(
        "Python programming",
        unrelated_memory,
    )

    assert matching_score > unrelated_score


def test_importance_affects_score():
    scorer = MemoryScorer()

    low_importance = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="AURA memory system",
        importance=0.1,
    )

    high_importance = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="AURA memory system",
        importance=0.9,
    )

    low_score = scorer.score(
        "AURA memory system",
        low_importance,
    )

    high_score = scorer.score(
        "AURA memory system",
        high_importance,
    )

    assert high_score > low_score


def test_recent_memory_scores_higher():
    scorer = MemoryScorer()

    recent_memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="AURA project",
        created_at=datetime.now(UTC),
    )

    old_memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="AURA project",
        created_at=(
            datetime.now(UTC)
            - timedelta(days=30)
        ),
    )

    recent_score = scorer.score(
        "AURA project",
        recent_memory,
    )

    old_score = scorer.score(
        "AURA project",
        old_memory,
    )

    assert recent_score > old_score


def test_access_frequency_affects_score():
    scorer = MemoryScorer()

    unused_memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="AURA system",
        access_count=0,
    )

    frequently_used_memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="AURA system",
        access_count=10,
    )

    unused_score = scorer.score(
        "AURA system",
        unused_memory,
    )

    used_score = scorer.score(
        "AURA system",
        frequently_used_memory,
    )

    assert used_score > unused_score


def test_rank_returns_highest_score_first():
    scorer = MemoryScorer()

    memories = [
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Football is a sport.",
        ),
        MemoryRecord(
            memory_type=MemoryType.PROJECT,
            content="AURA uses Python and FastAPI.",
            importance=0.9,
        ),
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Bananas are fruit.",
        ),
    ]

    ranked = scorer.rank(
        "AURA Python FastAPI",
        memories,
    )

    assert len(ranked) == 3

    top_memory, top_score = ranked[0]

    assert top_memory.content == (
        "AURA uses Python and FastAPI."
    )

    assert top_score > 0


def test_score_is_between_zero_and_one():
    scorer = MemoryScorer()

    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="AURA memory",
        importance=1.0,
        access_count=10,
    )

    score = scorer.score(
        "AURA memory",
        memory,
    )

    assert 0.0 <= score <= 1.0
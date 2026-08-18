from aura.memory.formatter import MemoryFormatter
from aura.memory.models import MemoryRecord, MemoryType


def test_format_single_memory():
    formatter = MemoryFormatter()

    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="AURA uses SQLite.",
        importance=0.8,
    )

    result = formatter.format_memory(
        memory
    )

    assert "Type: fact" in result
    assert "Content: AURA uses SQLite." in result
    assert "Importance: 0.80" in result


def test_format_memory_with_score():
    formatter = MemoryFormatter()

    memory = MemoryRecord(
        memory_type=MemoryType.PROJECT,
        content="AURA uses FastAPI.",
        importance=0.9,
    )

    result = formatter.format_memory(
        memory,
        score=0.8754,
    )

    assert "Relevance: 0.8754" in result


def test_format_memory_with_metadata():
    formatter = MemoryFormatter()

    memory = MemoryRecord(
        memory_type=MemoryType.PROJECT,
        content="AURA project memory.",
        metadata={
            "project": "AURA",
            "source": "test",
        },
    )

    result = formatter.format_memory(
        memory
    )

    assert "Metadata:" in result
    assert "project=AURA" in result
    assert "source=test" in result


def test_format_ranked_memories():
    formatter = MemoryFormatter()

    memory_one = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="Python is a programming language.",
    )

    memory_two = MemoryRecord(
        memory_type=MemoryType.PROJECT,
        content="AURA uses FastAPI.",
    )

    memories = [
        (
            memory_one,
            0.9,
        ),
        (
            memory_two,
            0.7,
        ),
    ]

    result = formatter.format_ranked_memories(
        memories
    )

    assert "Memory 1" in result
    assert "Memory 2" in result

    assert (
        "Python is a programming language."
        in result
    )

    assert "AURA uses FastAPI." in result


def test_format_ranked_memories_empty():
    formatter = MemoryFormatter()

    result = formatter.format_ranked_memories(
        []
    )

    assert result == ""


def test_format_for_prompt():
    formatter = MemoryFormatter()

    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="AURA has persistent memory.",
        importance=0.9,
    )

    memories = [
        (
            memory,
            0.95,
        )
    ]

    result = formatter.format_for_prompt(
        memories
    )

    assert result.startswith(
        "Relevant memory context:"
    )

    assert (
        "AURA has persistent memory."
        in result
    )


def test_format_for_prompt_empty():
    formatter = MemoryFormatter()

    result = formatter.format_for_prompt(
        []
    )

    assert result == ""
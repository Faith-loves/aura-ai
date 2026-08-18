from aura.memory.models import MemoryRecord, MemoryType


def test_memory_record_creation():
    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="Python is a programming language.",
    )

    assert memory.id is not None
    assert memory.memory_type == MemoryType.FACT
    assert memory.content == (
        "Python is a programming language."
    )

    assert memory.importance == 0.5
    assert memory.access_count == 0
    assert memory.metadata == {}


def test_memory_record_custom_importance():
    memory = MemoryRecord(
        memory_type=MemoryType.PROJECT,
        content="AURA is an autonomous AI system.",
        importance=0.9,
    )

    assert memory.importance == 0.9


def test_all_memory_types_exist():
    assert MemoryType.CONVERSATION.value == "conversation"
    assert MemoryType.FACT.value == "fact"
    assert MemoryType.PREFERENCE.value == "preference"
    assert MemoryType.PROJECT.value == "project"
    assert MemoryType.TASK.value == "task"
    assert MemoryType.SYSTEM.value == "system"
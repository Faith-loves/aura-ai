from aura.memory.models import MemoryRecord, MemoryType
from aura.memory.repository import MemoryRepository


def create_repository(tmp_path):
    database_path = tmp_path / "test_memory.db"

    return MemoryRepository(
        database_path=str(database_path)
    )


def test_repository_creates_database(tmp_path):
    repository = create_repository(tmp_path)

    assert repository.database_path.exists()


def test_save_and_get_memory(tmp_path):
    repository = create_repository(tmp_path)

    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="AURA uses persistent memory.",
        importance=0.8,
    )

    repository.save(memory)

    loaded = repository.get_by_id(
        memory.id
    )

    assert loaded is not None
    assert loaded.id == memory.id
    assert loaded.content == (
        "AURA uses persistent memory."
    )
    assert loaded.memory_type == MemoryType.FACT
    assert loaded.importance == 0.8


def test_list_all_memories(tmp_path):
    repository = create_repository(tmp_path)

    repository.save(
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="First memory",
        )
    )

    repository.save(
        MemoryRecord(
            memory_type=MemoryType.PROJECT,
            content="Second memory",
        )
    )

    memories = repository.list_all()

    assert len(memories) == 2


def test_list_memories_by_type(tmp_path):
    repository = create_repository(tmp_path)

    repository.save(
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Python is a language.",
        )
    )

    repository.save(
        MemoryRecord(
            memory_type=MemoryType.PROJECT,
            content="AURA project information.",
        )
    )

    facts = repository.list_by_type(
        MemoryType.FACT
    )

    assert len(facts) == 1
    assert facts[0].memory_type == MemoryType.FACT


def test_mark_memory_accessed(tmp_path):
    repository = create_repository(tmp_path)

    memory = MemoryRecord(
        memory_type=MemoryType.CONVERSATION,
        content="Previous conversation.",
    )

    repository.save(memory)

    updated = repository.mark_accessed(
        memory.id
    )

    assert updated is not None
    assert updated.access_count == 1
    assert updated.last_accessed_at is not None


def test_delete_memory(tmp_path):
    repository = create_repository(tmp_path)

    memory = MemoryRecord(
        memory_type=MemoryType.TASK,
        content="Temporary task.",
    )

    repository.save(memory)

    deleted = repository.delete(
        memory.id
    )

    assert deleted is True

    loaded = repository.get_by_id(
        memory.id
    )

    assert loaded is None


def test_repository_count(tmp_path):
    repository = create_repository(tmp_path)

    assert repository.count() == 0

    repository.save(
        MemoryRecord(
            memory_type=MemoryType.SYSTEM,
            content="System memory.",
        )
    )

    assert repository.count() == 1

def test_find_exact_memory(tmp_path):
    repository = create_repository(tmp_path)

    memory = MemoryRecord(
        memory_type=MemoryType.PROJECT,
        content="AURA uses FastAPI.",
    )

    repository.save(memory)

    found = repository.find_exact(
        content="AURA uses FastAPI.",
        memory_type=MemoryType.PROJECT,
    )

    assert found is not None
    assert found.id == memory.id


def test_find_exact_memory_is_case_insensitive(
    tmp_path,
):
    repository = create_repository(tmp_path)

    memory = MemoryRecord(
        memory_type=MemoryType.FACT,
        content="Python is useful.",
    )

    repository.save(memory)

    found = repository.find_exact(
        content="python is useful.",
        memory_type=MemoryType.FACT,
    )

    assert found is not None
    assert found.id == memory.id


def test_find_exact_memory_returns_none(
    tmp_path,
):
    repository = create_repository(tmp_path)

    found = repository.find_exact(
        content="Missing memory.",
        memory_type=MemoryType.FACT,
    )

    assert found is None
    
def test_count_by_type(tmp_path):
    repository = create_repository(tmp_path)

    repository.save(
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Fact one",
        )
    )

    repository.save(
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Fact two",
        )
    )

    repository.save(
        MemoryRecord(
            memory_type=MemoryType.PROJECT,
            content="Project one",
        )
    )

    counts = repository.count_by_type()

    assert counts["fact"] == 2
    assert counts["project"] == 1


def test_most_accessed(tmp_path):
    repository = create_repository(tmp_path)

    first = repository.save(
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="First",
            access_count=1,
        )
    )

    second = repository.save(
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="Second",
            access_count=10,
        )
    )

    results = repository.most_accessed(
        limit=1
    )

    assert len(results) == 1
    assert results[0].id == second.id

def test_clear_all_memories(tmp_path):
    repository = create_repository(tmp_path)

    repository.save(
        MemoryRecord(
            memory_type=MemoryType.FACT,
            content="First memory",
        )
    )

    repository.save(
        MemoryRecord(
            memory_type=MemoryType.PROJECT,
            content="Second memory",
        )
    )

    assert repository.count() == 2

    deleted = repository.clear_all()

    assert deleted == 2
    assert repository.count() == 0
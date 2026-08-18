from aura.memory.formatter import MemoryFormatter
from aura.memory.manager import MemoryManager
from aura.memory.models import MemoryType
from aura.memory.repository import MemoryRepository
from aura.memory.scorer import MemoryScorer


def create_memory_manager(tmp_path):
    database_path = tmp_path / "manager_memory.db"

    repository = MemoryRepository(
        database_path=str(database_path)
    )

    scorer = MemoryScorer()
    formatter = MemoryFormatter()

    return MemoryManager(
        repository=repository,
        scorer=scorer,
        formatter=formatter,
    )


def test_remember_memory(tmp_path):
    manager = create_memory_manager(tmp_path)

    memory = manager.remember(
        content="AURA uses SQLite memory.",
        memory_type=MemoryType.FACT,
        importance=0.8,
    )

    assert memory.id is not None
    assert memory.content == (
        "AURA uses SQLite memory."
    )
    assert memory.memory_type == MemoryType.FACT
    assert memory.importance == 0.8
    assert manager.count() == 1


def test_recall_memory(tmp_path):
    manager = create_memory_manager(tmp_path)

    memory = manager.remember(
        content="Remember this information.",
        memory_type=MemoryType.CONVERSATION,
    )

    recalled = manager.recall(
        memory.id
    )

    assert recalled is not None
    assert recalled.id == memory.id
    assert recalled.content == (
        "Remember this information."
    )
    assert recalled.access_count == 1
    assert recalled.last_accessed_at is not None


def test_recall_without_marking_access(tmp_path):
    manager = create_memory_manager(tmp_path)

    memory = manager.remember(
        content="Do not increase access count.",
        memory_type=MemoryType.FACT,
    )

    recalled = manager.recall(
        memory.id,
        mark_accessed=False,
    )

    assert recalled is not None
    assert recalled.access_count == 0
    assert recalled.last_accessed_at is None


def test_recall_unknown_memory(tmp_path):
    manager = create_memory_manager(tmp_path)

    recalled = manager.recall(
        "unknown-memory-id"
    )

    assert recalled is None


def test_list_all_memories(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="Fact memory",
        memory_type=MemoryType.FACT,
    )

    manager.remember(
        content="Project memory",
        memory_type=MemoryType.PROJECT,
    )

    memories = manager.list_memories()

    assert len(memories) == 2


def test_list_memories_by_type(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="Python fact",
        memory_type=MemoryType.FACT,
    )

    manager.remember(
        content="AURA project",
        memory_type=MemoryType.PROJECT,
    )

    facts = manager.list_memories(
        MemoryType.FACT
    )

    assert len(facts) == 1
    assert facts[0].memory_type == MemoryType.FACT


def test_forget_memory(tmp_path):
    manager = create_memory_manager(tmp_path)

    memory = manager.remember(
        content="Delete this memory.",
        memory_type=MemoryType.TASK,
    )

    deleted = manager.forget(
        memory.id
    )

    assert deleted is True
    assert manager.count() == 0


def test_memory_metadata(tmp_path):
    manager = create_memory_manager(tmp_path)

    memory = manager.remember(
        content="Project-specific memory.",
        memory_type=MemoryType.PROJECT,
        metadata={
            "project": "AURA",
            "source": "test",
        },
    )

    assert memory.metadata["project"] == "AURA"
    assert memory.metadata["source"] == "test"


def test_search_returns_relevant_memory_first(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="Football is a popular sport.",
        memory_type=MemoryType.FACT,
    )

    manager.remember(
        content="AURA uses Python and FastAPI.",
        memory_type=MemoryType.PROJECT,
        importance=0.9,
    )

    manager.remember(
        content="Bananas are yellow fruit.",
        memory_type=MemoryType.FACT,
    )

    results = manager.search(
        query="AURA Python FastAPI",
        limit=3,
        mark_accessed=False,
    )

    assert len(results) == 3

    top_memory, top_score = results[0]

    assert top_memory.content == (
        "AURA uses Python and FastAPI."
    )

    assert top_score > 0


def test_search_respects_limit(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="Python memory one.",
        memory_type=MemoryType.FACT,
    )

    manager.remember(
        content="Python memory two.",
        memory_type=MemoryType.FACT,
    )

    manager.remember(
        content="Python memory three.",
        memory_type=MemoryType.FACT,
    )

    results = manager.search(
        query="Python",
        limit=2,
        mark_accessed=False,
    )

    assert len(results) == 2


def test_search_filters_by_memory_type(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA Python fact.",
        memory_type=MemoryType.FACT,
    )

    manager.remember(
        content="AURA Python project.",
        memory_type=MemoryType.PROJECT,
    )

    results = manager.search(
        query="AURA Python",
        memory_type=MemoryType.PROJECT,
        mark_accessed=False,
    )

    assert len(results) == 1

    memory, score = results[0]

    assert memory.memory_type == MemoryType.PROJECT
    assert score > 0


def test_search_marks_memories_as_accessed(tmp_path):
    manager = create_memory_manager(tmp_path)

    memory = manager.remember(
        content="AURA memory search.",
        memory_type=MemoryType.FACT,
    )

    results = manager.search(
        query="AURA memory",
        limit=1,
        mark_accessed=True,
    )

    assert len(results) == 1

    result_memory, _ = results[0]

    assert result_memory.id == memory.id
    assert result_memory.access_count == 1
    assert result_memory.last_accessed_at is not None


def test_search_can_skip_access_tracking(tmp_path):
    manager = create_memory_manager(tmp_path)

    memory = manager.remember(
        content="AURA memory search.",
        memory_type=MemoryType.FACT,
    )

    manager.search(
        query="AURA memory",
        limit=1,
        mark_accessed=False,
    )

    stored_memory = manager.recall(
        memory.id,
        mark_accessed=False,
    )

    assert stored_memory is not None
    assert stored_memory.access_count == 0


def test_search_empty_repository(tmp_path):
    manager = create_memory_manager(tmp_path)

    results = manager.search(
        query="AURA",
    )

    assert results == []


def test_search_zero_limit_returns_empty_list(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA memory.",
        memory_type=MemoryType.FACT,
    )

    results = manager.search(
        query="AURA",
        limit=0,
    )

    assert results == []


def test_build_context(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA uses persistent SQLite memory.",
        memory_type=MemoryType.PROJECT,
        importance=0.9,
    )

    manager.remember(
        content="FastAPI powers the AURA API.",
        memory_type=MemoryType.PROJECT,
        importance=0.8,
    )

    context = manager.build_context(
        query="AURA FastAPI memory",
        limit=2,
        mark_accessed=False,
    )

    assert context.startswith(
        "Relevant memory context:"
    )

    assert (
        "AURA uses persistent SQLite memory."
        in context
    )


def test_build_context_empty_repository(tmp_path):
    manager = create_memory_manager(tmp_path)

    context = manager.build_context(
        query="AURA",
    )

    assert context == ""


def test_build_context_respects_memory_type(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA general fact.",
        memory_type=MemoryType.FACT,
    )

    manager.remember(
        content="AURA project architecture.",
        memory_type=MemoryType.PROJECT,
    )

    context = manager.build_context(
        query="AURA",
        memory_type=MemoryType.PROJECT,
        mark_accessed=False,
    )

    assert "AURA project architecture." in context
    assert "AURA general fact." not in context


def test_remember_does_not_create_exact_duplicate(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    first = manager.remember(
        content="AURA uses FastAPI.",
        memory_type=MemoryType.PROJECT,
        importance=0.5,
    )

    second = manager.remember(
        content="AURA uses FastAPI.",
        memory_type=MemoryType.PROJECT,
        importance=0.5,
    )

    assert first.id == second.id
    assert manager.count() == 1


def test_duplicate_memory_keeps_higher_importance(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    first = manager.remember(
        content="AURA uses SQLite.",
        memory_type=MemoryType.PROJECT,
        importance=0.5,
    )

    second = manager.remember(
        content="AURA uses SQLite.",
        memory_type=MemoryType.PROJECT,
        importance=0.9,
    )

    assert first.id == second.id
    assert second.importance == 0.9
    assert manager.count() == 1


def test_duplicate_memory_merges_metadata(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    first = manager.remember(
        content="AURA uses Python.",
        memory_type=MemoryType.PROJECT,
        metadata={
            "source": "conversation",
        },
    )

    second = manager.remember(
        content="AURA uses Python.",
        memory_type=MemoryType.PROJECT,
        metadata={
            "confirmed": True,
        },
    )

    assert first.id == second.id

    assert (
        second.metadata["source"]
        == "conversation"
    )

    assert (
        second.metadata["confirmed"]
        is True
    )

    assert manager.count() == 1


def test_same_content_different_type_is_not_duplicate(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA uses Python.",
        memory_type=MemoryType.FACT,
    )

    manager.remember(
        content="AURA uses Python.",
        memory_type=MemoryType.PROJECT,
    )

    assert manager.count() == 2

def test_content_similarity_identical_text(tmp_path):
    manager = create_memory_manager(tmp_path)

    score = manager._content_similarity(
        "AURA uses FastAPI and SQLite.",
        "AURA uses FastAPI and SQLite.",
    )

    assert score == 1.0


def test_content_similarity_ignores_case_and_punctuation(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    score = manager._content_similarity(
        "AURA uses FastAPI!",
        "aura uses fastapi.",
    )

    assert score == 1.0


def test_content_similarity_ignores_word_order(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    score = manager._content_similarity(
        "AURA uses FastAPI and SQLite.",
        "AURA uses SQLite and FastAPI.",
    )

    assert score == 1.0


def test_content_similarity_different_memories(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    score = manager._content_similarity(
        "AURA uses FastAPI.",
        "Football matches are exciting.",
    )

    assert score < 0.75


def test_find_near_duplicate(tmp_path):
    manager = create_memory_manager(tmp_path)

    original = manager.remember(
        content="AURA uses FastAPI and SQLite.",
        memory_type=MemoryType.PROJECT,
    )

    duplicate = manager.find_near_duplicate(
        content="AURA uses SQLite and FastAPI.",
        memory_type=MemoryType.PROJECT,
    )

    assert duplicate is not None
    assert duplicate.id == original.id


def test_find_near_duplicate_returns_none_for_different_memory(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA uses FastAPI and SQLite.",
        memory_type=MemoryType.PROJECT,
    )

    duplicate = manager.find_near_duplicate(
        content="The weather is sunny today.",
        memory_type=MemoryType.PROJECT,
    )

    assert duplicate is None


def test_remember_does_not_create_near_duplicate(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    first = manager.remember(
        content="AURA uses FastAPI and SQLite.",
        memory_type=MemoryType.PROJECT,
        importance=0.6,
    )

    second = manager.remember(
        content="AURA uses SQLite and FastAPI.",
        memory_type=MemoryType.PROJECT,
        importance=0.8,
    )

    assert first.id == second.id
    assert manager.count() == 1
    assert second.importance == 0.8


def test_near_duplicate_keeps_original_content(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA uses FastAPI and SQLite.",
        memory_type=MemoryType.PROJECT,
    )

    manager.remember(
        content="AURA uses SQLite and FastAPI.",
        memory_type=MemoryType.PROJECT,
    )

    memories = manager.list_memories(
        MemoryType.PROJECT
    )

    assert len(memories) == 1

    assert memories[0].content == (
        "AURA uses FastAPI and SQLite."
    )


def test_same_words_different_memory_types_are_not_merged(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA uses FastAPI and SQLite.",
        memory_type=MemoryType.FACT,
    )

    manager.remember(
        content="AURA uses SQLite and FastAPI.",
        memory_type=MemoryType.PROJECT,
    )

    assert manager.count() == 2
    
def test_project_memory_update_replaces_old_value(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    old_memory = manager.remember(
        content="My project uses Flask.",
        memory_type=MemoryType.PROJECT,
        importance=0.6,
    )

    updated_memory = manager.remember(
        content="My project now uses FastAPI.",
        memory_type=MemoryType.PROJECT,
        importance=0.8,
    )

    assert old_memory.id == updated_memory.id

    assert updated_memory.content == (
        "My project now uses FastAPI."
    )

    assert updated_memory.importance == 0.8

    assert manager.count() == 1


def test_updated_memory_keeps_previous_content(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="My project uses Flask.",
        memory_type=MemoryType.PROJECT,
    )

    updated = manager.remember(
        content="My project now uses FastAPI.",
        memory_type=MemoryType.PROJECT,
    )

    assert (
        updated.metadata["previous_content"]
        == "My project uses Flask."
    )

    assert updated.metadata["updated"] is True


def test_updated_memory_has_update_timestamp(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="My project uses Flask.",
        memory_type=MemoryType.PROJECT,
    )

    updated = manager.remember(
        content="My project now uses FastAPI.",
        memory_type=MemoryType.PROJECT,
    )

    assert "updated_at" in updated.metadata


def test_unrelated_projects_do_not_conflict(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA uses FastAPI.",
        memory_type=MemoryType.PROJECT,
    )

    manager.remember(
        content="SentinelX uses Python.",
        memory_type=MemoryType.PROJECT,
    )

    assert manager.count() == 2


def test_conversation_memories_are_not_conflict_replaced(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="Can you explain FastAPI?",
        memory_type=MemoryType.CONVERSATION,
    )

    manager.remember(
        content="Can you explain Django?",
        memory_type=MemoryType.CONVERSATION,
    )

    assert manager.count() == 2


def test_preference_update_replaces_old_preference(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    first = manager.remember(
        content="I prefer Python.",
        memory_type=MemoryType.PREFERENCE,
    )

    second = manager.remember(
        content="I prefer TypeScript.",
        memory_type=MemoryType.PREFERENCE,
    )

    assert first.id == second.id
    assert second.content == "I prefer TypeScript."
    assert manager.count() == 1
    
def test_memory_statistics(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA project memory.",
        memory_type=MemoryType.PROJECT,
        importance=0.9,
    )

    manager.remember(
        content="AURA fact memory.",
        memory_type=MemoryType.FACT,
        importance=0.5,
    )

    stats = manager.get_statistics()

    assert stats["total"] == 2
    assert stats["by_type"]["project"] == 1
    assert stats["by_type"]["fact"] == 1
    assert stats["average_importance"] == 0.7


def test_cleanup_keeps_recent_memory(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="Recent low-value memory.",
        memory_type=MemoryType.CONVERSATION,
        importance=0.1,
    )

    deleted = manager.cleanup(
        min_importance=0.3,
        max_access_count=0,
        older_than_days=30,
    )

    assert deleted == 0
    assert manager.count() == 1
def test_cleanup_contaminated_memories(
    tmp_path,
):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content=(
            "Relevant memory context:\n\n"
            "Memory 1\n"
            "Content: AURA uses FastAPI.\n\n"
            "Current user request:\n"
            "Hello"
        ),
        memory_type=MemoryType.CONVERSATION,
    )

    manager.remember(
        content="AURA uses FastAPI.",
        memory_type=MemoryType.PROJECT,
    )

    deleted = (
        manager.cleanup_contaminated_memories()
    )

    assert deleted == 1
    assert manager.count() == 1

    remaining = manager.list_memories()

    assert remaining[0].content == (
        "AURA uses FastAPI."
    )
def test_export_memories(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="AURA uses FastAPI.",
        memory_type=MemoryType.PROJECT,
        importance=0.9,
    )

    exported = manager.export_memories()

    assert exported["version"] == 1
    assert exported["count"] == 1
    assert len(exported["memories"]) == 1

    assert (
        exported["memories"][0]["content"]
        == "AURA uses FastAPI."
    )


def test_export_to_file(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="Export test memory.",
        memory_type=MemoryType.FACT,
    )

    output_path = (
        tmp_path / "memory_export.json"
    )

    result = manager.export_to_file(
        str(output_path)
    )

    assert result.exists()

    assert (
        output_path.read_text(
            encoding="utf-8"
        )
    )


def test_import_memories(tmp_path):
    manager = create_memory_manager(tmp_path)

    source = manager.remember(
        content="Import this memory.",
        memory_type=MemoryType.FACT,
        importance=0.8,
    )

    exported = manager.export_memories()

    second_repository = MemoryRepository(
        database_path=str(
            tmp_path / "imported.db"
        )
    )

    second_manager = MemoryManager(
        repository=second_repository,
        scorer=MemoryScorer(),
        formatter=MemoryFormatter(),
    )

    imported = second_manager.import_memories(
        exported
    )

    assert imported == 1
    assert second_manager.count() == 1

    loaded = second_manager.recall(
        source.id,
        mark_accessed=False,
    )

    assert loaded is not None
    assert loaded.content == (
        "Import this memory."
    )


def test_import_preserves_metadata(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="Metadata backup.",
        memory_type=MemoryType.PROJECT,
        metadata={
            "project": "AURA",
            "source": "test",
        },
    )

    exported = manager.export_memories()

    second_repository = MemoryRepository(
        database_path=str(
            tmp_path / "metadata_import.db"
        )
    )

    second_manager = MemoryManager(
        repository=second_repository,
        scorer=MemoryScorer(),
        formatter=MemoryFormatter(),
    )

    second_manager.import_memories(
        exported
    )

    memories = second_manager.list_memories()

    assert len(memories) == 1

    assert (
        memories[0].metadata["project"]
        == "AURA"
    )


def test_create_backup(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="Backup memory.",
        memory_type=MemoryType.FACT,
    )

    backup_path = manager.create_backup(
        backup_directory=str(
            tmp_path / "backups"
        )
    )

    assert backup_path.exists()

    assert backup_path.suffix == ".json"

def test_clear_all_memories(tmp_path):
    manager = create_memory_manager(tmp_path)

    manager.remember(
        content="First memory.",
        memory_type=MemoryType.FACT,
    )

    manager.remember(
        content="Second memory.",
        memory_type=MemoryType.PROJECT,
    )

    deleted = manager.clear_all_memories()

    assert deleted == 2
    assert manager.count() == 0


def test_restore_from_file_replaces_existing_memory(
    tmp_path,
):
    source_repository = MemoryRepository(
        database_path=str(
            tmp_path / "source.db"
        )
    )

    source_manager = MemoryManager(
        repository=source_repository,
        scorer=MemoryScorer(),
        formatter=MemoryFormatter(),
    )

    source_manager.remember(
        content="Restored AURA memory.",
        memory_type=MemoryType.PROJECT,
        importance=0.9,
    )

    backup_path = source_manager.create_backup(
        backup_directory=str(
            tmp_path / "backups"
        )
    )

    target_repository = MemoryRepository(
        database_path=str(
            tmp_path / "target.db"
        )
    )

    target_manager = MemoryManager(
        repository=target_repository,
        scorer=MemoryScorer(),
        formatter=MemoryFormatter(),
    )

    target_manager.remember(
        content="Old memory.",
        memory_type=MemoryType.FACT,
    )

    result = target_manager.restore_from_file(
        file_path=str(backup_path),
        clear_existing=True,
    )

    assert result["previous_count"] == 1
    assert result["cleared"] == 1
    assert result["imported"] == 1
    assert result["current_count"] == 1

    memories = target_manager.list_memories()

    assert len(memories) == 1
    assert memories[0].content == (
        "Restored AURA memory."
    )
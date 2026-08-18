from aura.execution.models import (
    Execution,
    ExecutionStatus,
)
from aura.execution.store import (
    ExecutionStore,
)


def create_execution(
    plan_id: str = "plan-1",
    goal: str = "Build API",
) -> Execution:
    return Execution(
        plan_id=plan_id,
        goal=goal,
    )


def test_store_starts_empty():
    store = ExecutionStore()

    assert (
        store.count()
        == 0
    )

    assert (
        store.list_all()
        == []
    )


def test_save_execution():
    store = ExecutionStore()

    execution = create_execution()

    saved = store.save(
        execution
    )

    assert saved is execution

    assert (
        store.count()
        == 1
    )

    assert (
        store.exists(
            execution.id
        )
        is True
    )


def test_get_execution():
    store = ExecutionStore()

    execution = create_execution()

    store.save(
        execution
    )

    result = store.get(
        execution.id
    )

    assert result is execution


def test_get_unknown_execution_returns_none():
    store = ExecutionStore()

    assert (
        store.get(
            "missing"
        )
        is None
    )


def test_execution_exists():
    store = ExecutionStore()

    execution = create_execution()

    store.save(
        execution
    )

    assert (
        store.exists(
            execution.id
        )
        is True
    )

    assert (
        store.exists(
            "missing"
        )
        is False
    )


def test_list_all_executions():
    store = ExecutionStore()

    first = create_execution(
        plan_id="plan-1",
        goal="First",
    )

    second = create_execution(
        plan_id="plan-2",
        goal="Second",
    )

    store.save(
        first
    )

    store.save(
        second
    )

    executions = (
        store.list_all()
    )

    assert len(
        executions
    ) == 2

    assert first in executions
    assert second in executions


def test_list_by_status():
    store = ExecutionStore()

    pending = create_execution(
        plan_id="plan-1",
        goal="Pending",
    )

    running = create_execution(
        plan_id="plan-2",
        goal="Running",
    )

    completed = create_execution(
        plan_id="plan-3",
        goal="Completed",
    )

    running.start()

    completed.start()
    completed.complete()

    store.save(
        pending
    )

    store.save(
        running
    )

    store.save(
        completed
    )

    pending_results = (
        store.list_by_status(
            ExecutionStatus.PENDING
        )
    )

    running_results = (
        store.list_by_status(
            ExecutionStatus.RUNNING
        )
    )

    completed_results = (
        store.list_by_status(
            ExecutionStatus.COMPLETED
        )
    )

    assert pending_results == [
        pending
    ]

    assert running_results == [
        running
    ]

    assert completed_results == [
        completed
    ]


def test_save_updates_existing_execution():
    store = ExecutionStore()

    execution = create_execution()

    store.save(
        execution
    )

    execution.start()

    store.save(
        execution
    )

    assert (
        store.count()
        == 1
    )

    stored = store.get(
        execution.id
    )

    assert stored is not None

    assert (
        stored.status
        == ExecutionStatus.RUNNING
    )


def test_delete_execution():
    store = ExecutionStore()

    execution = create_execution()

    store.save(
        execution
    )

    deleted = store.delete(
        execution.id
    )

    assert deleted is True

    assert (
        store.count()
        == 0
    )

    assert (
        store.get(
            execution.id
        )
        is None
    )


def test_delete_unknown_execution_returns_false():
    store = ExecutionStore()

    deleted = store.delete(
        "missing"
    )

    assert deleted is False


def test_clear_execution_store():
    store = ExecutionStore()

    store.save(
        create_execution(
            plan_id="plan-1",
            goal="First",
        )
    )

    store.save(
        create_execution(
            plan_id="plan-2",
            goal="Second",
        )
    )

    removed = store.clear()

    assert removed == 2

    assert (
        store.count()
        == 0
    )

    assert (
        store.list_all()
        == []
    )


def test_status_filter_returns_empty_list():
    store = ExecutionStore()

    execution = create_execution()

    store.save(
        execution
    )

    results = store.list_by_status(
        ExecutionStatus.FAILED
    )

    assert results == []
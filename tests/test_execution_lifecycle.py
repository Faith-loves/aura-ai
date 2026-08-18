import pytest

from aura.execution.manager import ExecutionManager
from aura.execution.models import (
    ExecutionStatus,
    StepExecutionStatus,
)
from aura.execution.store import ExecutionStore
from aura.planning.models import (
    Plan,
    PlanStatus,
    PlanStep,
)
from aura.planning.planner import Planner


def create_manager():
    planner = Planner()

    store = ExecutionStore()

    manager = ExecutionManager(
        store=store,
        planner=planner,
    )

    return manager, planner


def create_plan():
    first = PlanStep(
        title="First step",
        priority=5,
    )

    second = PlanStep(
        title="Second step",
        priority=4,
        dependencies=[
            first.id
        ],
    )

    return Plan(
        goal="Lifecycle test",
        steps=[
            first,
            second,
        ],
    )


def test_start_execution():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution=execution,
        plan=plan,
    )

    assert (
        execution.status
        == ExecutionStatus.RUNNING
    )

    assert (
        plan.status
        == PlanStatus.IN_PROGRESS
    )

    assert (
        execution.step_executions[0]
        .status
        == StepExecutionStatus.READY
    )

    assert (
        execution.step_executions[1]
        .status
        == StepExecutionStatus.PENDING
    )


def test_only_pending_execution_can_start():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution,
        plan,
    )

    with pytest.raises(
        ValueError,
        match="Only pending executions",
    ):
        manager.start_execution(
            execution,
            plan,
        )


def test_pause_execution():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution,
        plan,
    )

    manager.pause_execution(
        execution
    )

    assert (
        execution.status
        == ExecutionStatus.PAUSED
    )


def test_only_running_execution_can_pause():
    manager, _ = create_manager()

    execution = (
        manager.create_execution(
            create_plan()
        )
    )

    with pytest.raises(
        ValueError,
        match="Only running executions",
    ):
        manager.pause_execution(
            execution
        )


def test_resume_execution():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution,
        plan,
    )

    manager.pause_execution(
        execution
    )

    manager.resume_execution(
        execution
    )

    assert (
        execution.status
        == ExecutionStatus.RUNNING
    )


def test_only_paused_execution_can_resume():
    manager, _ = create_manager()

    execution = (
        manager.create_execution(
            create_plan()
        )
    )

    with pytest.raises(
        ValueError,
        match="Only paused executions",
    ):
        manager.resume_execution(
            execution
        )


def test_complete_execution():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution,
        plan,
    )

    for step_execution in (
        execution.step_executions
    ):
        step_execution.start()
        step_execution.complete()

    manager.complete_execution(
        execution=execution,
        plan=plan,
    )

    assert (
        execution.status
        == ExecutionStatus.COMPLETED
    )

    assert (
        plan.status
        == PlanStatus.COMPLETED
    )

    assert (
        execution.completed_at
        is not None
    )


def test_cannot_complete_with_unfinished_steps():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution,
        plan,
    )

    with pytest.raises(
        ValueError,
        match="unfinished steps",
    ):
        manager.complete_execution(
            execution,
            plan,
        )


def test_fail_execution():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution,
        plan,
    )

    manager.fail_execution(
        execution=execution,
        plan=plan,
        error="Something failed.",
        error_code="execution_failed",
    )

    assert (
        execution.status
        == ExecutionStatus.FAILED
    )

    assert (
        execution.error
        == "Something failed."
    )

    assert (
        execution.error_code
        == "execution_failed"
    )

    assert (
        plan.status
        == PlanStatus.FAILED
    )


def test_cancel_execution():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution,
        plan,
    )

    manager.cancel_execution(
        execution=execution,
        plan=plan,
    )

    assert (
        execution.status
        == ExecutionStatus.CANCELLED
    )

    assert (
        plan.status
        == PlanStatus.CANCELLED
    )


def test_terminal_execution_cannot_fail_again():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution,
        plan,
    )

    manager.fail_execution(
        execution,
        plan,
        error="Failed.",
    )

    with pytest.raises(
        ValueError,
        match="terminal state",
    ):
        manager.fail_execution(
            execution,
            plan,
            error="Failed again.",
        )


def test_terminal_execution_cannot_cancel():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution,
        plan,
    )

    manager.cancel_execution(
        execution,
        plan,
    )

    with pytest.raises(
        ValueError,
        match="terminal state",
    ):
        manager.cancel_execution(
            execution,
            plan,
        )


def test_execution_and_plan_must_match():
    manager, _ = create_manager()

    first_plan = create_plan()

    second_plan = create_plan()

    execution = (
        manager.create_execution(
            first_plan
        )
    )

    with pytest.raises(
        ValueError,
        match="does not belong",
    ):
        manager.start_execution(
            execution,
            second_plan,
        )


def test_lifecycle_changes_are_saved():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    manager.start_execution(
        execution,
        plan,
    )

    stored = manager.store.get(
        execution.id
    )

    assert stored is not None

    assert (
        stored.status
        == ExecutionStatus.RUNNING
    )

    manager.pause_execution(
        execution
    )

    stored = manager.store.get(
        execution.id
    )

    assert (
        stored.status
        == ExecutionStatus.PAUSED
    )
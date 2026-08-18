import pytest

from aura.execution.manager import ExecutionManager
from aura.execution.models import (
    ExecutionStatus,
    StepExecutionStatus,
)
from aura.execution.store import ExecutionStore
from aura.planning.models import (
    Plan,
    PlanStep,
    PlanStepStatus,
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

    third = PlanStep(
        title="Third step",
        priority=3,
        dependencies=[
            second.id
        ],
    )

    return Plan(
        goal="Execute steps",
        steps=[
            first,
            second,
            third,
        ],
    )


def create_running_execution():
    manager, planner = (
        create_manager()
    )

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

    return (
        manager,
        planner,
        plan,
        execution,
    )


def test_get_next_step():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    result = manager.get_next_step(
        execution=execution,
        plan=plan,
    )

    assert result is not None

    plan_step, step_execution = (
        result
    )

    assert (
        plan_step.id
        == plan.steps[0].id
    )

    assert (
        step_execution.plan_step_id
        == plan.steps[0].id
    )

    assert (
        step_execution.status
        == StepExecutionStatus.READY
    )


def test_start_next_step():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    step_execution = (
        manager.start_next_step(
            execution=execution,
            plan=plan,
        )
    )

    assert step_execution is not None

    assert (
        step_execution.status
        == StepExecutionStatus.RUNNING
    )

    assert (
        plan.steps[0].status
        == PlanStepStatus.IN_PROGRESS
    )

    assert (
        execution.current_step_id
        == plan.steps[0].id
    )


def test_complete_current_step():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    manager.start_next_step(
        execution,
        plan,
    )

    completed = (
        manager.complete_current_step(
            execution=execution,
            plan=plan,
            output={
                "result": "done"
            },
            tool_execution_id=(
                "tool-exec-1"
            ),
        )
    )

    assert (
        completed.status
        == StepExecutionStatus.COMPLETED
    )

    assert completed.output == {
        "result": "done"
    }

    assert (
        completed.tool_execution_id
        == "tool-exec-1"
    )

    assert (
        plan.steps[0].status
        == PlanStepStatus.COMPLETED
    )

    assert (
        execution.current_step_id
        is None
    )

    assert (
        execution.step_executions[1]
        .status
        == StepExecutionStatus.READY
    )


def test_next_step_advances_after_completion():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    first = (
        manager.start_next_step(
            execution,
            plan,
        )
    )

    manager.complete_current_step(
        execution,
        plan,
    )

    second = (
        manager.start_next_step(
            execution,
            plan,
        )
    )

    assert first is not None
    assert second is not None

    assert (
        first.plan_step_id
        == plan.steps[0].id
    )

    assert (
        second.plan_step_id
        == plan.steps[1].id
    )


def test_fail_current_step():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    manager.start_next_step(
        execution,
        plan,
    )

    failed = (
        manager.fail_current_step(
            execution=execution,
            plan=plan,
            error="Tool failed.",
            error_code="tool_failed",
            tool_execution_id=(
                "tool-exec-2"
            ),
        )
    )

    assert (
        failed.status
        == StepExecutionStatus.FAILED
    )

    assert (
        failed.error
        == "Tool failed."
    )

    assert (
        failed.error_code
        == "tool_failed"
    )

    assert (
        plan.steps[0].status
        == PlanStepStatus.FAILED
    )

    assert (
        execution.current_step_id
        is None
    )


def test_skip_current_step():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    manager.start_next_step(
        execution,
        plan,
    )

    skipped = (
        manager.skip_current_step(
            execution=execution,
            plan=plan,
        )
    )

    assert (
        skipped.status
        == StepExecutionStatus.SKIPPED
    )

    assert (
        plan.steps[0].status
        == PlanStepStatus.SKIPPED
    )

    assert (
        execution.current_step_id
        is None
    )


def test_cannot_complete_without_current_step():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    with pytest.raises(
        ValueError,
        match="no current step",
    ):
        manager.complete_current_step(
            execution,
            plan,
        )


def test_cannot_fail_without_current_step():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    with pytest.raises(
        ValueError,
        match="no current step",
    ):
        manager.fail_current_step(
            execution,
            plan,
            error="Failed",
        )


def test_pending_execution_cannot_get_next_step():
    manager, _ = create_manager()

    plan = create_plan()

    execution = (
        manager.create_execution(
            plan
        )
    )

    with pytest.raises(
        ValueError,
        match="must be running",
    ):
        manager.get_next_step(
            execution,
            plan,
        )


def test_no_ready_step_returns_none():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    first = (
        manager.start_next_step(
            execution,
            plan,
        )
    )

    assert first is not None

    result = manager.get_next_step(
        execution,
        plan,
    )

    assert result is None


def test_steps_can_run_to_completion():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    while True:
        step = (
            manager.start_next_step(
                execution,
                plan,
            )
        )

        if step is None:
            break

        manager.complete_current_step(
            execution,
            plan,
            output=(
                f"Completed "
                f"{step.title}"
            ),
        )

    assert all(
        step.status
        == StepExecutionStatus.COMPLETED
        for step
        in execution.step_executions
    )

    manager.complete_execution(
        execution,
        plan,
    )

    assert (
        execution.status
        == ExecutionStatus.COMPLETED
    )


def test_cannot_pause_with_running_step():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    manager.start_next_step(
        execution,
        plan,
    )

    with pytest.raises(
        ValueError,
        match="while a step is running",
    ):
        manager.pause_execution(
            execution
        )


def test_step_changes_are_saved():
    (
        manager,
        _,
        plan,
        execution,
    ) = create_running_execution()

    manager.start_next_step(
        execution,
        plan,
    )

    stored = manager.store.get(
        execution.id
    )

    assert stored is not None

    assert (
        stored.current_step_id
        == plan.steps[0].id
    )

    manager.complete_current_step(
        execution,
        plan,
    )

    stored = manager.store.get(
        execution.id
    )

    assert (
        stored.step_executions[0]
        .status
        == StepExecutionStatus.COMPLETED
    )
import pytest

from aura.execution.models import (
    Execution,
    ExecutionStatus,
    StepExecution,
    StepExecutionStatus,
)


def test_execution_creation():
    execution = Execution(
        plan_id="plan-1",
        goal="Build a REST API.",
    )

    assert execution.id

    assert (
        execution.plan_id
        == "plan-1"
    )

    assert (
        execution.goal
        == "Build a REST API."
    )

    assert (
        execution.status
        == ExecutionStatus.PENDING
    )

    assert (
        execution.step_executions
        == []
    )

    assert (
        execution.current_step_id
        is None
    )


def test_execution_ids_are_unique():
    first = Execution(
        plan_id="plan-1",
        goal="First goal",
    )

    second = Execution(
        plan_id="plan-2",
        goal="Second goal",
    )

    assert first.id != second.id


def test_step_execution_creation():
    step = StepExecution(
        plan_step_id="step-1",
        title="Define requirements",
    )

    assert step.id

    assert (
        step.plan_step_id
        == "step-1"
    )

    assert (
        step.title
        == "Define requirements"
    )

    assert (
        step.status
        == StepExecutionStatus.PENDING
    )

    assert step.tool_name is None

    assert step.arguments == {}


def test_step_can_be_marked_ready():
    step = StepExecution(
        plan_step_id="step-1",
        title="First step",
    )

    step.mark_ready()

    assert (
        step.status
        == StepExecutionStatus.READY
    )


def test_step_can_start():
    step = StepExecution(
        plan_step_id="step-1",
        title="First step",
    )

    step.start()

    assert (
        step.status
        == StepExecutionStatus.RUNNING
    )

    assert step.started_at is not None


def test_step_can_complete():
    step = StepExecution(
        plan_step_id="step-1",
        title="First step",
    )

    step.start()

    step.complete(
        output={
            "result": "done"
        },
        tool_execution_id="tool-exec-1",
    )

    assert (
        step.status
        == StepExecutionStatus.COMPLETED
    )

    assert step.output == {
        "result": "done"
    }

    assert (
        step.tool_execution_id
        == "tool-exec-1"
    )

    assert (
        step.completed_at
        is not None
    )

    assert (
        step.duration_ms
        is not None
    )

    assert step.error is None


def test_step_can_fail():
    step = StepExecution(
        plan_step_id="step-1",
        title="First step",
    )

    step.start()

    step.fail(
        error="Tool failed.",
        error_code="tool_failed",
        tool_execution_id="tool-exec-2",
    )

    assert (
        step.status
        == StepExecutionStatus.FAILED
    )

    assert (
        step.error
        == "Tool failed."
    )

    assert (
        step.error_code
        == "tool_failed"
    )

    assert (
        step.tool_execution_id
        == "tool-exec-2"
    )

    assert (
        step.completed_at
        is not None
    )


def test_step_can_be_skipped():
    step = StepExecution(
        plan_step_id="step-1",
        title="Optional step",
    )

    step.skip()

    assert (
        step.status
        == StepExecutionStatus.SKIPPED
    )

    assert (
        step.completed_at
        is not None
    )


def test_execution_can_start():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    execution.start()

    assert (
        execution.status
        == ExecutionStatus.RUNNING
    )

    assert (
        execution.started_at
        is not None
    )


def test_execution_can_pause():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    execution.start()

    execution.pause()

    assert (
        execution.status
        == ExecutionStatus.PAUSED
    )


def test_execution_can_complete():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    execution.start()

    execution.complete()

    assert (
        execution.status
        == ExecutionStatus.COMPLETED
    )

    assert (
        execution.completed_at
        is not None
    )

    assert (
        execution.duration_ms
        is not None
    )

    assert (
        execution.current_step_id
        is None
    )


def test_execution_can_fail():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    execution.start()

    execution.fail(
        error="Execution failed.",
        error_code="execution_failed",
    )

    assert (
        execution.status
        == ExecutionStatus.FAILED
    )

    assert (
        execution.error
        == "Execution failed."
    )

    assert (
        execution.error_code
        == "execution_failed"
    )

    assert (
        execution.completed_at
        is not None
    )


def test_execution_can_cancel():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    execution.start()

    execution.cancel()

    assert (
        execution.status
        == ExecutionStatus.CANCELLED
    )

    assert (
        execution.completed_at
        is not None
    )


def test_add_step_execution():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    step = StepExecution(
        plan_step_id="step-1",
        title="First step",
    )

    execution.add_step_execution(
        step
    )

    assert (
        len(
            execution.step_executions
        )
        == 1
    )

    assert (
        execution.step_executions[0]
        is step
    )


def test_duplicate_plan_step_execution_fails():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    first = StepExecution(
        plan_step_id="step-1",
        title="First",
    )

    second = StepExecution(
        plan_step_id="step-1",
        title="Duplicate",
    )

    execution.add_step_execution(
        first
    )

    with pytest.raises(
        ValueError,
        match=(
            "already has an execution record"
        ),
    ):
        execution.add_step_execution(
            second
        )


def test_get_step_execution():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    step = StepExecution(
        plan_step_id="step-1",
        title="First",
    )

    execution.add_step_execution(
        step
    )

    result = (
        execution.get_step_execution(
            "step-1"
        )
    )

    assert result is step


def test_unknown_step_execution_returns_none():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    assert (
        execution.get_step_execution(
            "missing"
        )
        is None
    )


def test_set_current_step():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    step = StepExecution(
        plan_step_id="step-1",
        title="First",
    )

    execution.add_step_execution(
        step
    )

    execution.set_current_step(
        "step-1"
    )

    assert (
        execution.current_step_id
        == "step-1"
    )


def test_set_unknown_current_step_fails():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    with pytest.raises(
        ValueError,
        match=(
            "does not contain plan step"
        ),
    ):
        execution.set_current_step(
            "missing"
        )


def test_clear_current_step():
    execution = Execution(
        plan_id="plan-1",
        goal="Build API",
    )

    step = StepExecution(
        plan_step_id="step-1",
        title="First",
    )

    execution.add_step_execution(
        step
    )

    execution.set_current_step(
        "step-1"
    )

    execution.set_current_step(
        None
    )

    assert (
        execution.current_step_id
        is None
    )
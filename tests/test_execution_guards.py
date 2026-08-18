import pytest

from aura.execution.guards import (
    ExecutionGuard,
    ExecutionLimits,
)
from aura.execution.models import (
    Execution,
    StepExecution,
    StepExecutionStatus,
)


def create_execution(
    step_count: int = 2,
) -> Execution:
    execution = Execution(
        plan_id="plan-1",
        goal="Guard test",
    )

    for index in range(
        step_count
    ):
        execution.add_step_execution(
            StepExecution(
                plan_step_id=(
                    f"step-{index}"
                ),
                title=(
                    f"Step {index}"
                ),
            )
        )

    return execution


def test_limits_reject_zero_steps():
    with pytest.raises(
        ValueError,
        match="max_steps",
    ):
        ExecutionLimits(
            max_steps=0
        )


def test_limits_reject_zero_failures():
    with pytest.raises(
        ValueError,
        match="max_failures",
    ):
        ExecutionLimits(
            max_failures=0
        )


def test_limits_reject_zero_iterations():
    with pytest.raises(
        ValueError,
        match="max_iterations",
    ):
        ExecutionLimits(
            max_iterations=0
        )


def test_execution_within_step_limit_passes():
    execution = create_execution(
        step_count=2
    )

    guard = ExecutionGuard(
        ExecutionLimits(
            max_steps=3
        )
    )

    guard.validate_before_run(
        execution
    )


def test_execution_over_step_limit_fails():
    execution = create_execution(
        step_count=3
    )

    guard = ExecutionGuard(
        ExecutionLimits(
            max_steps=2
        )
    )

    with pytest.raises(
        ValueError,
        match="maximum step limit",
    ):
        guard.validate_before_run(
            execution
        )


def test_iteration_limit():
    execution = create_execution()

    guard = ExecutionGuard(
        ExecutionLimits(
            max_iterations=2
        )
    )

    guard.validate_iteration(
        execution,
        iteration=1,
    )

    guard.validate_iteration(
        execution,
        iteration=2,
    )

    with pytest.raises(
        ValueError,
        match="maximum iteration limit",
    ):
        guard.validate_iteration(
            execution,
            iteration=3,
        )


def test_failure_limit():
    execution = create_execution(
        step_count=3
    )

    execution.step_executions[
        0
    ].status = (
        StepExecutionStatus.FAILED
    )

    execution.step_executions[
        1
    ].status = (
        StepExecutionStatus.FAILED
    )

    guard = ExecutionGuard(
        ExecutionLimits(
            max_failures=2
        )
    )

    with pytest.raises(
        ValueError,
        match="maximum failure limit",
    ):
        guard.validate_iteration(
            execution,
            iteration=1,
        )


def test_count_failures():
    execution = create_execution(
        step_count=3
    )

    execution.step_executions[
        0
    ].status = (
        StepExecutionStatus.FAILED
    )

    guard = ExecutionGuard()

    assert (
        guard.count_failures(
            execution
        )
        == 1
    )


def test_count_completed_steps():
    execution = create_execution(
        step_count=3
    )

    execution.step_executions[
        0
    ].status = (
        StepExecutionStatus.COMPLETED
    )

    execution.step_executions[
        1
    ].status = (
        StepExecutionStatus.SKIPPED
    )

    guard = ExecutionGuard()

    assert (
        guard.count_completed_steps(
            execution
        )
        == 2
    )
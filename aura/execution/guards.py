from dataclasses import dataclass

from aura.execution.models import (
    Execution,
    StepExecutionStatus,
)


@dataclass
class ExecutionLimits:
    max_steps: int = 50
    max_failures: int = 3
    max_iterations: int = 100

    def __post_init__(
        self,
    ) -> None:
        if self.max_steps < 1:
            raise ValueError(
                "max_steps must be at least 1."
            )

        if self.max_failures < 1:
            raise ValueError(
                "max_failures must be at least 1."
            )

        if self.max_iterations < 1:
            raise ValueError(
                "max_iterations must be at least 1."
            )


class ExecutionGuard:
    def __init__(
        self,
        limits: ExecutionLimits | None = None,
    ):
        self.limits = (
            limits
            or ExecutionLimits()
        )

    def validate_before_run(
        self,
        execution: Execution,
    ) -> None:
        total_steps = len(
            execution.step_executions
        )

        if (
            total_steps
            > self.limits.max_steps
        ):
            raise ValueError(
                "Execution exceeds maximum "
                f"step limit of "
                f"{self.limits.max_steps}."
            )

    def validate_iteration(
        self,
        execution: Execution,
        iteration: int,
    ) -> None:
        if (
            iteration
            > self.limits.max_iterations
        ):
            raise ValueError(
                "Execution exceeded maximum "
                f"iteration limit of "
                f"{self.limits.max_iterations}."
            )

        failure_count = (
            self.count_failures(
                execution
            )
        )

        if (
            failure_count
            >= self.limits.max_failures
        ):
            raise ValueError(
                "Execution reached maximum "
                f"failure limit of "
                f"{self.limits.max_failures}."
            )

    def count_failures(
        self,
        execution: Execution,
    ) -> int:
        return sum(
            1
            for step
            in execution.step_executions
            if (
                step.status
                == StepExecutionStatus.FAILED
            )
        )

    def count_completed_steps(
        self,
        execution: Execution,
    ) -> int:
        return sum(
            1
            for step
            in execution.step_executions
            if step.status in {
                StepExecutionStatus.COMPLETED,
                StepExecutionStatus.SKIPPED,
            }
        )
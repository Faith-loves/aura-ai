from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepExecutionStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepExecution(BaseModel):
    id: str = Field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    plan_step_id: str = Field(
        ...,
        min_length=1,
    )

    title: str = Field(
        ...,
        min_length=1,
    )

    status: StepExecutionStatus = (
        StepExecutionStatus.PENDING
    )

    tool_name: str | None = None

    arguments: dict[str, Any] = Field(
        default_factory=dict
    )

    tool_execution_id: str | None = None

    output: Any | None = None

    error: str | None = None

    error_code: str | None = None

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_ms: float | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    def mark_ready(
        self,
    ) -> None:
        self.status = (
            StepExecutionStatus.READY
        )

    def start(
        self,
    ) -> None:
        self.status = (
            StepExecutionStatus.RUNNING
        )

        self.started_at = datetime.now(
            UTC
        )

        self.completed_at = None

        self.duration_ms = None

    def complete(
        self,
        output: Any | None = None,
        tool_execution_id: str | None = None,
    ) -> None:
        self.status = (
            StepExecutionStatus.COMPLETED
        )

        self.output = output

        self.tool_execution_id = (
            tool_execution_id
        )

        self.error = None
        self.error_code = None

        self._finish_timing()

    def fail(
        self,
        error: str,
        error_code: str | None = None,
        tool_execution_id: str | None = None,
    ) -> None:
        self.status = (
            StepExecutionStatus.FAILED
        )

        self.error = error

        self.error_code = error_code

        self.tool_execution_id = (
            tool_execution_id
        )

        self._finish_timing()

    def skip(
        self,
    ) -> None:
        self.status = (
            StepExecutionStatus.SKIPPED
        )

        self._finish_timing()

    def _finish_timing(
        self,
    ) -> None:
        completed_at = datetime.now(
            UTC
        )

        self.completed_at = completed_at

        if self.started_at is None:
            self.started_at = completed_at
            self.duration_ms = 0.0
            return

        self.duration_ms = (
            completed_at - self.started_at
        ).total_seconds() * 1000


class Execution(BaseModel):
    id: str = Field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    plan_id: str = Field(
        ...,
        min_length=1,
    )

    goal: str = Field(
        ...,
        min_length=1,
    )

    status: ExecutionStatus = (
        ExecutionStatus.PENDING
    )

    step_executions: list[
        StepExecution
    ] = Field(
        default_factory=list
    )

    current_step_id: str | None = None

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_ms: float | None = None

    error: str | None = None

    error_code: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    def start(
        self,
    ) -> None:
        self.status = (
            ExecutionStatus.RUNNING
        )

        self.started_at = datetime.now(
            UTC
        )

        self.completed_at = None
        self.duration_ms = None
        self.error = None
        self.error_code = None

    def pause(
        self,
    ) -> None:
        self.status = (
            ExecutionStatus.PAUSED
        )

    def complete(
        self,
    ) -> None:
        self.status = (
            ExecutionStatus.COMPLETED
        )

        self.current_step_id = None

        self.error = None
        self.error_code = None

        self._finish_timing()

    def fail(
        self,
        error: str,
        error_code: str | None = None,
    ) -> None:
        self.status = (
            ExecutionStatus.FAILED
        )

        self.error = error
        self.error_code = error_code

        self.current_step_id = None

        self._finish_timing()

    def cancel(
        self,
    ) -> None:
        self.status = (
            ExecutionStatus.CANCELLED
        )

        self.current_step_id = None

        self._finish_timing()

    def add_step_execution(
        self,
        step_execution: StepExecution,
    ) -> None:
        if any(
            existing.id
            == step_execution.id
            for existing
            in self.step_executions
        ):
            raise ValueError(
                f"Step execution "
                f"'{step_execution.id}' "
                "already exists."
            )

        if any(
            existing.plan_step_id
            == step_execution.plan_step_id
            for existing
            in self.step_executions
        ):
            raise ValueError(
                f"Plan step "
                f"'{step_execution.plan_step_id}' "
                "already has an execution record."
            )

        self.step_executions.append(
            step_execution
        )

    def get_step_execution(
        self,
        plan_step_id: str,
    ) -> StepExecution | None:
        for step_execution in (
            self.step_executions
        ):
            if (
                step_execution.plan_step_id
                == plan_step_id
            ):
                return step_execution

        return None

    def set_current_step(
        self,
        plan_step_id: str | None,
    ) -> None:
        if plan_step_id is None:
            self.current_step_id = None
            return

        step_execution = (
            self.get_step_execution(
                plan_step_id
            )
        )

        if step_execution is None:
            raise ValueError(
                f"Execution does not contain "
                f"plan step '{plan_step_id}'."
            )

        self.current_step_id = (
            plan_step_id
        )

    def _finish_timing(
        self,
    ) -> None:
        completed_at = datetime.now(
            UTC
        )

        self.completed_at = completed_at

        if self.started_at is None:
            self.started_at = completed_at
            self.duration_ms = 0.0
            return

        self.duration_ms = (
            completed_at - self.started_at
        ).total_seconds() * 1000
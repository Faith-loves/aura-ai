from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from aura.execution.models import (
    ExecutionStatus,
    StepExecutionStatus,
)


class CreateExecutionRequest(BaseModel):
    plan_id: str = Field(
        ...,
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class StepExecutionResponse(BaseModel):
    id: str
    plan_step_id: str
    title: str

    status: StepExecutionStatus

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


class ExecutionResponse(BaseModel):
    id: str

    plan_id: str

    goal: str

    status: ExecutionStatus

    step_executions: list[
        StepExecutionResponse
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
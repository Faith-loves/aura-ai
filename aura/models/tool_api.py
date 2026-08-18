from typing import Any

from pydantic import BaseModel, Field

from aura.tools.models import (
    ToolExecutionStatus,
)


class ExecuteToolRequest(BaseModel):
    arguments: dict[str, Any] = Field(
        default_factory=dict
    )


class ToolResponse(BaseModel):
    name: str
    description: str
    category: str
    version: str
    dangerous: bool
    requires_confirmation: bool
    tags: list[str]
    parameters: list[dict]


class ToolExecutionResponse(BaseModel):
    execution_id: str
    tool_name: str | None = None
    status: ToolExecutionStatus | None = None
    success: bool
    output: Any | None = None
    error: str | None = None
    error_code: str | None = None
    started_at: str
    completed_at: str | None = None
    duration_ms: float | None = None
    metadata: dict = Field(
        default_factory=dict
    )
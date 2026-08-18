from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ToolParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    OBJECT = "object"


class ToolExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class ToolParameter(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
    )

    description: str = ""

    parameter_type: ToolParameterType = (
        ToolParameterType.STRING
    )

    required: bool = True

    default: Any | None = None

    choices: list[Any] | None = None


class ToolMetadata(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
    )

    description: str = Field(
        ...,
        min_length=1,
    )

    category: str = "general"

    version: str = "1.0.0"

    dangerous: bool = False

    requires_confirmation: bool = False

    tags: list[str] = Field(
        default_factory=list
    )

    parameters: list[
        ToolParameter
    ] = Field(
        default_factory=list
    )


class ToolResult(BaseModel):
    execution_id: str = Field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    tool_name: str | None = None

    status: ToolExecutionStatus | None = None

    success: bool

    output: Any | None = None

    error: str | None = None

    error_code: str | None = None

    started_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC
        )
    )

    completed_at: datetime | None = None

    duration_ms: float | None = None

    metadata: dict = Field(
        default_factory=dict
    )
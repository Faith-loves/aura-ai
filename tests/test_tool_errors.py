import pytest

from aura.tools.base import Tool
from aura.tools.errors import (
    ToolErrorCode,
    ToolExecutionError,
    ToolNotFoundError,
    ToolValidationError,
)
from aura.tools.executor import ToolExecutor
from aura.tools.models import (
    ToolParameter,
    ToolParameterType,
    ToolResult,
)
from aura.tools.registry import ToolRegistry


class RequiredArgumentTool(Tool):
    @property
    def name(self) -> str:
        return "required"

    @property
    def description(self) -> str:
        return "Requires one argument."

    @property
    def parameters(
        self,
    ) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="value",
                parameter_type=(
                    ToolParameterType.STRING
                ),
                required=True,
            )
        ]

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            output=kwargs["value"],
        )


class CrashingTool(Tool):
    @property
    def name(self) -> str:
        return "crashing"

    @property
    def description(self) -> str:
        return "Raises an error."

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        raise RuntimeError(
            "Tool crashed."
        )


class FailedResultTool(Tool):
    @property
    def name(self) -> str:
        return "failed_result"

    @property
    def description(self) -> str:
        return "Returns failure."

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=False,
            error="Tool could not complete.",
        )


class InvalidResultTool(Tool):
    @property
    def name(self) -> str:
        return "invalid"

    @property
    def description(self) -> str:
        return "Returns invalid result."

    async def execute(
        self,
        **kwargs,
    ):
        return "wrong"


def create_executor():
    registry = ToolRegistry()

    registry.register(
        RequiredArgumentTool()
    )

    registry.register(
        CrashingTool()
    )

    registry.register(
        FailedResultTool()
    )

    registry.register(
        InvalidResultTool()
    )

    return ToolExecutor(
        registry=registry
    )


def test_tool_not_found_error():
    error = ToolNotFoundError(
        "missing"
    )

    assert (
        error.code
        == ToolErrorCode.TOOL_NOT_FOUND
    )

    assert (
        error.message
        == "Tool 'missing' is not registered."
    )


def test_tool_validation_error():
    error = ToolValidationError(
        "Invalid argument."
    )

    assert (
        error.code
        == ToolErrorCode.VALIDATION_ERROR
    )

    assert (
        error.message
        == "Invalid argument."
    )


def test_tool_execution_error():
    error = ToolExecutionError(
        "Execution failed."
    )

    assert (
        error.code
        == ToolErrorCode.EXECUTION_ERROR
    )


@pytest.mark.anyio
async def test_unknown_tool_returns_error_code():
    executor = create_executor()

    result = await executor.execute(
        "missing"
    )

    assert result.success is False

    assert (
        result.error_code
        == "tool_not_found"
    )

    assert (
        result.metadata["stage"]
        == "lookup"
    )


@pytest.mark.anyio
async def test_validation_failure_returns_error_code():
    executor = create_executor()

    result = await executor.execute(
        "required",
        arguments={},
    )

    assert result.success is False

    assert (
        result.error_code
        == "validation_error"
    )

    assert (
        result.metadata["stage"]
        == "validation"
    )


@pytest.mark.anyio
async def test_execution_failure_returns_error_code():
    executor = create_executor()

    result = await executor.execute(
        "crashing"
    )

    assert result.success is False

    assert (
        result.error_code
        == "execution_error"
    )

    assert (
        result.metadata["stage"]
        == "execution"
    )


@pytest.mark.anyio
async def test_invalid_result_returns_error_code():
    executor = create_executor()

    result = await executor.execute(
        "invalid"
    )

    assert result.success is False

    assert (
        result.error_code
        == "invalid_result"
    )

    assert (
        result.metadata["stage"]
        == "result"
    )


@pytest.mark.anyio
async def test_tool_reported_failure_gets_error_code():
    executor = create_executor()

    result = await executor.execute(
        "failed_result"
    )

    assert result.success is False

    assert (
        result.error_code
        == "tool_failed"
    )

    assert (
        result.error
        == "Tool could not complete."
    )

    assert (
        result.metadata["stage"]
        == "tool_result"
    )


@pytest.mark.anyio
async def test_successful_tool_has_no_error_code():
    executor = create_executor()

    result = await executor.execute(
        "required",
        arguments={
            "value": "AURA",
        },
    )

    assert result.success is True
    assert result.error_code is None
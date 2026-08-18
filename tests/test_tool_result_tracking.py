import pytest

from aura.tools.base import Tool
from aura.tools.executor import ToolExecutor
from aura.tools.models import (
    ToolExecutionStatus,
    ToolResult,
)
from aura.tools.registry import ToolRegistry


class SuccessTool(Tool):
    @property
    def name(self) -> str:
        return "success_tool"

    @property
    def description(self) -> str:
        return "Successful test tool."

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            output="done",
        )


class FailureResultTool(Tool):
    @property
    def name(self) -> str:
        return "failure_result"

    @property
    def description(self) -> str:
        return "Returns a failed result."

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=False,
            error="Operation failed.",
        )


class ExceptionTool(Tool):
    @property
    def name(self) -> str:
        return "exception_tool"

    @property
    def description(self) -> str:
        return "Raises an exception."

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        raise RuntimeError(
            "Execution crashed."
        )


def create_executor():
    registry = ToolRegistry()

    registry.register(
        SuccessTool()
    )

    registry.register(
        FailureResultTool()
    )

    registry.register(
        ExceptionTool()
    )

    return ToolExecutor(
        registry=registry
    )


def test_tool_result_has_execution_id():
    result = ToolResult(
        success=True
    )

    assert result.execution_id


def test_execution_ids_are_unique():
    first = ToolResult(
        success=True
    )

    second = ToolResult(
        success=True
    )

    assert (
        first.execution_id
        != second.execution_id
    )


@pytest.mark.anyio
async def test_successful_execution_tracking():
    executor = create_executor()

    result = await executor.execute(
        "success_tool"
    )

    assert result.success is True

    assert (
        result.status
        == ToolExecutionStatus.SUCCESS
    )

    assert (
        result.tool_name
        == "success_tool"
    )

    assert (
        result.completed_at
        is not None
    )

    assert (
        result.duration_ms
        is not None
    )

    assert result.error_code is None


@pytest.mark.anyio
async def test_failed_tool_result_tracking():
    executor = create_executor()

    result = await executor.execute(
        "failure_result"
    )

    assert result.success is False

    assert (
        result.status
        == ToolExecutionStatus.FAILED
    )

    assert (
        result.error_code
        == "tool_failed"
    )


@pytest.mark.anyio
async def test_exception_execution_tracking():
    executor = create_executor()

    result = await executor.execute(
        "exception_tool"
    )

    assert result.success is False

    assert (
        result.error_code
        == "execution_error"
    )

    assert (
        result.metadata[
            "exception_type"
        ]
        == "RuntimeError"
    )


@pytest.mark.anyio
async def test_unknown_tool_has_tracking_data():
    executor = create_executor()

    result = await executor.execute(
        "missing_tool"
    )

    assert result.success is False

    assert (
        result.error_code
        == "tool_not_found"
    )

    assert (
        result.completed_at
        is not None
    )


@pytest.mark.anyio
async def test_success_metadata_contains_tool_name():
    executor = create_executor()

    result = await executor.execute(
        "success_tool"
    )

    assert (
        result.metadata["tool"]
        == "success_tool"
    )

    assert (
        result.metadata["stage"]
        == "completed"
    )
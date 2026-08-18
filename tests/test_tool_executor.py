import pytest

from aura.tools.base import Tool
from aura.tools.executor import ToolExecutor
from aura.tools.models import (
    ToolExecutionStatus,
    ToolParameter,
    ToolParameterType,
    ToolResult,
)
from aura.tools.registry import ToolRegistry
from aura.tools.validator import (
    ToolArgumentValidator,
)


class EchoTool(Tool):
    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return (
            "Return the supplied message."
        )

    @property
    def parameters(
        self,
    ) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="message",
                description="Message to return.",
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
            output=kwargs["message"],
        )


class FailingTool(Tool):
    @property
    def name(self) -> str:
        return "failing"

    @property
    def description(self) -> str:
        return (
            "Tool that raises an exception."
        )

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        raise RuntimeError(
            "Tool crashed."
        )


class InvalidResultTool(Tool):
    @property
    def name(self) -> str:
        return "invalid_result"

    @property
    def description(self) -> str:
        return (
            "Returns the wrong result type."
        )

    async def execute(
        self,
        **kwargs,
    ):
        return "invalid"


class DefaultArgumentTool(Tool):
    @property
    def name(self) -> str:
        return "default_argument"

    @property
    def description(self) -> str:
        return (
            "Tests default arguments."
        )

    @property
    def parameters(
        self,
    ) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="message",
                parameter_type=(
                    ToolParameterType.STRING
                ),
                required=True,
            ),
            ToolParameter(
                name="count",
                parameter_type=(
                    ToolParameterType.INTEGER
                ),
                required=False,
                default=2,
            ),
        ]

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            output={
                "message":
                    kwargs["message"],
                "count":
                    kwargs["count"],
            },
        )


def create_executor():
    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    registry.register(
        FailingTool()
    )

    registry.register(
        InvalidResultTool()
    )

    registry.register(
        DefaultArgumentTool()
    )

    return ToolExecutor(
        registry=registry,
        validator=(
            ToolArgumentValidator()
        ),
    )


@pytest.mark.anyio
async def test_execute_registered_tool():
    executor = create_executor()

    result = await executor.execute(
        tool_name="echo",
        arguments={
            "message": "Hello AURA",
        },
    )

    assert result.success is True

    assert (
        result.status
        == ToolExecutionStatus.SUCCESS
    )

    assert (
        result.output
        == "Hello AURA"
    )

    assert (
        result.tool_name
        == "echo"
    )

    assert (
        result.metadata["stage"]
        == "completed"
    )


@pytest.mark.anyio
async def test_unknown_tool_returns_failure():
    executor = create_executor()

    result = await executor.execute(
        tool_name="missing",
        arguments={},
    )

    assert result.success is False

    assert (
        result.status
        == ToolExecutionStatus.FAILED
    )

    assert (
        result.error
        == "Tool 'missing' is not registered."
    )


@pytest.mark.anyio
async def test_missing_required_argument_returns_failure():
    executor = create_executor()

    result = await executor.execute(
        tool_name="echo",
        arguments={},
    )

    assert result.success is False

    assert (
        "Missing required argument"
        in result.error
    )

    assert (
        result.metadata["stage"]
        == "validation"
    )


@pytest.mark.anyio
async def test_invalid_argument_type_returns_failure():
    executor = create_executor()

    result = await executor.execute(
        tool_name="echo",
        arguments={
            "message": 123,
        },
    )

    assert result.success is False

    assert (
        "must be of type 'string'"
        in result.error
    )


@pytest.mark.anyio
async def test_unexpected_argument_returns_failure():
    executor = create_executor()

    result = await executor.execute(
        tool_name="echo",
        arguments={
            "message": "Hello",
            "unknown": "value",
        },
    )

    assert result.success is False

    assert (
        "Unexpected argument"
        in result.error
    )


@pytest.mark.anyio
async def test_tool_exception_returns_failure():
    executor = create_executor()

    result = await executor.execute(
        tool_name="failing",
        arguments={},
    )

    assert result.success is False

    assert (
        result.error
        == "Tool crashed."
    )

    assert (
        result.metadata["stage"]
        == "execution"
    )


@pytest.mark.anyio
async def test_invalid_tool_result_returns_failure():
    executor = create_executor()

    result = await executor.execute(
        tool_name="invalid_result",
        arguments={},
    )

    assert result.success is False

    assert (
        "invalid result"
        in result.error
    )

    assert (
        result.metadata["stage"]
        == "result"
    )


@pytest.mark.anyio
async def test_default_arguments_are_passed_to_tool():
    executor = create_executor()

    result = await executor.execute(
        tool_name="default_argument",
        arguments={
            "message": "AURA",
        },
    )

    assert result.success is True

    assert result.output == {
        "message": "AURA",
        "count": 2,
    }


@pytest.mark.anyio
async def test_execution_has_timestamps():
    executor = create_executor()

    result = await executor.execute(
        tool_name="echo",
        arguments={
            "message": "AURA",
        },
    )

    assert (
        result.started_at
        is not None
    )

    assert (
        result.completed_at
        is not None
    )

    assert (
        result.duration_ms
        is not None
    )


@pytest.mark.anyio
async def test_execution_id_is_created():
    executor = create_executor()

    result = await executor.execute(
        tool_name="echo",
        arguments={
            "message": "AURA",
        },
    )

    assert result.execution_id
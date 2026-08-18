import pytest

from aura.tools.base import Tool
from aura.tools.models import (
    ToolParameter,
    ToolParameterType,
    ToolResult,
)


class ExampleTool(Tool):
    @property
    def name(self) -> str:
        return "example"

    @property
    def description(self) -> str:
        return (
            "Example tool used for testing."
        )

    @property
    def parameters(
        self,
    ) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="message",
                description=(
                    "Message to return."
                ),
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
        message = kwargs.get(
            "message"
        )

        return ToolResult(
            success=True,
            output=message,
            metadata={
                "tool": self.name,
            },
        )


def test_tool_parameter_creation():
    parameter = ToolParameter(
        name="query",
        description="Search query.",
        parameter_type=(
            ToolParameterType.STRING
        ),
        required=True,
    )

    assert parameter.name == "query"

    assert (
        parameter.parameter_type
        == ToolParameterType.STRING
    )

    assert parameter.required is True
    assert parameter.default is None


def test_tool_result_success():
    result = ToolResult(
        success=True,
        output="Completed",
    )

    assert result.success is True
    assert result.output == "Completed"
    assert result.error is None


def test_tool_result_failure():
    result = ToolResult(
        success=False,
        error="Something failed.",
    )

    assert result.success is False
    assert result.output is None

    assert (
        result.error
        == "Something failed."
    )


def test_example_tool_metadata():
    tool = ExampleTool()

    assert tool.name == "example"

    assert tool.description == (
        "Example tool used for testing."
    )

    assert len(
        tool.parameters
    ) == 1


def test_tool_schema():
    tool = ExampleTool()

    schema = tool.get_schema()

    assert schema["name"] == "example"

    assert schema["description"] == (
        "Example tool used for testing."
    )

    assert len(
        schema["parameters"]
    ) == 1

    assert (
        schema["parameters"][0]["name"]
        == "message"
    )

    assert (
        schema["parameters"][0]
        ["parameter_type"]
        == "string"
    )


def test_required_parameters():
    tool = ExampleTool()

    required = (
        tool.required_parameters()
    )

    assert required == [
        "message"
    ]


@pytest.mark.anyio
async def test_tool_execute():
    tool = ExampleTool()

    result = await tool.execute(
        message="Hello AURA"
    )

    assert result.success is True

    assert (
        result.output
        == "Hello AURA"
    )

    assert (
        result.metadata["tool"]
        == "example"
    )


def test_tool_cannot_be_instantiated_directly():
    with pytest.raises(
        TypeError
    ):
        Tool()
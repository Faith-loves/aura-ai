import pytest

from aura.tools.base import Tool
from aura.tools.models import (
    ToolMetadata,
    ToolParameter,
    ToolParameterType,
    ToolResult,
)


class SearchTool(Tool):
    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return (
            "Search for information."
        )

    @property
    def category(self) -> str:
        return "information"

    @property
    def version(self) -> str:
        return "1.1.0"

    @property
    def tags(self) -> list[str]:
        return [
            "search",
            "information",
        ]

    @property
    def parameters(
        self,
    ) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                description="Search query.",
                parameter_type=(
                    ToolParameterType.STRING
                ),
                required=True,
            ),
            ToolParameter(
                name="limit",
                description=(
                    "Maximum number of results."
                ),
                parameter_type=(
                    ToolParameterType.INTEGER
                ),
                required=False,
                default=5,
            ),
        ]

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            output={
                "query": kwargs.get(
                    "query"
                ),
                "limit": kwargs.get(
                    "limit",
                    5,
                ),
            },
        )


class DangerousTool(Tool):
    @property
    def name(self) -> str:
        return "dangerous_example"

    @property
    def description(self) -> str:
        return (
            "Example sensitive tool."
        )

    @property
    def dangerous(self) -> bool:
        return True

    @property
    def requires_confirmation(
        self,
    ) -> bool:
        return True

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            output="done",
        )


def test_tool_parameter_type_values():
    assert (
        ToolParameterType.STRING.value
        == "string"
    )

    assert (
        ToolParameterType.INTEGER.value
        == "integer"
    )

    assert (
        ToolParameterType.FLOAT.value
        == "float"
    )

    assert (
        ToolParameterType.BOOLEAN.value
        == "boolean"
    )

    assert (
        ToolParameterType.LIST.value
        == "list"
    )

    assert (
        ToolParameterType.OBJECT.value
        == "object"
    )


def test_tool_parameter_with_choices():
    parameter = ToolParameter(
        name="format",
        description="Output format.",
        parameter_type=(
            ToolParameterType.STRING
        ),
        choices=[
            "json",
            "text",
        ],
    )

    assert parameter.choices == [
        "json",
        "text",
    ]


def test_tool_metadata_creation():
    metadata = ToolMetadata(
        name="example",
        description="Example tool.",
        category="testing",
        tags=[
            "example"
        ],
    )

    assert metadata.name == "example"

    assert (
        metadata.category
        == "testing"
    )

    assert (
        metadata.version
        == "1.0.0"
    )

    assert (
        metadata.dangerous
        is False
    )


def test_search_tool_metadata():
    tool = SearchTool()

    metadata = tool.get_metadata()

    assert metadata.name == "search"

    assert (
        metadata.description
        == "Search for information."
    )

    assert (
        metadata.category
        == "information"
    )

    assert (
        metadata.version
        == "1.1.0"
    )

    assert metadata.tags == [
        "search",
        "information",
    ]

    assert len(
        metadata.parameters
    ) == 2


def test_search_tool_schema():
    tool = SearchTool()

    schema = tool.get_schema()

    assert schema["name"] == "search"

    assert (
        schema["category"]
        == "information"
    )

    assert (
        schema["parameters"][0]
        ["parameter_type"]
        == "string"
    )

    assert (
        schema["parameters"][1]
        ["parameter_type"]
        == "integer"
    )


def test_required_parameters_only_returns_required():
    tool = SearchTool()

    assert (
        tool.required_parameters()
        == ["query"]
    )


def test_dangerous_tool_metadata():
    tool = DangerousTool()

    metadata = tool.get_metadata()

    assert (
        metadata.dangerous
        is True
    )

    assert (
        metadata.requires_confirmation
        is True
    )


@pytest.mark.anyio
async def test_metadata_tool_executes():
    tool = SearchTool()

    result = await tool.execute(
        query="AURA",
        limit=3,
    )

    assert result.success is True

    assert result.output == {
        "query": "AURA",
        "limit": 3,
    }
import pytest

from aura.tools.base import Tool
from aura.tools.models import (
    ToolParameter,
    ToolParameterType,
    ToolResult,
)
from aura.tools.registry import ToolRegistry


class EchoTool(Tool):
    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return (
            "Returns the provided message."
        )

    @property
    def category(self) -> str:
        return "utility"

    @property
    def tags(self) -> list[str]:
        return [
            "echo",
            "utility",
        ]

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
        return ToolResult(
            success=True,
            output=kwargs.get(
                "message"
            ),
        )


class SecondEchoTool(Tool):
    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return (
            "Replacement echo tool."
        )

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            output="replacement",
        )


class CalculatorTool(Tool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "Performs calculations."
        )

    @property
    def category(self) -> str:
        return "utility"

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True,
            output=0,
        )


def test_registry_starts_empty():
    registry = ToolRegistry()

    assert registry.count() == 0
    assert registry.list_tools() == []
    assert registry.list_names() == []


def test_register_tool():
    registry = ToolRegistry()

    tool = EchoTool()

    registry.register(
        tool
    )

    assert registry.count() == 1

    assert registry.exists(
        "echo"
    ) is True

    assert (
        registry.get("echo")
        is tool
    )


def test_duplicate_tool_registration_fails():
    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(
            EchoTool()
        )


def test_registered_tool_can_be_replaced():
    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    replacement = SecondEchoTool()

    registry.register(
        replacement,
        replace=True,
    )

    assert registry.count() == 1

    assert (
        registry.get("echo")
        is replacement
    )

    assert (
        registry.get("echo").description
        == "Replacement echo tool."
    )


def test_get_unknown_tool_fails():
    registry = ToolRegistry()

    with pytest.raises(
        ValueError,
        match="is not registered",
    ):
        registry.get(
            "missing"
        )


def test_find_unknown_tool_returns_none():
    registry = ToolRegistry()

    assert (
        registry.find("missing")
        is None
    )


def test_unregister_tool():
    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    deleted = registry.unregister(
        "echo"
    )

    assert deleted is True
    assert registry.count() == 0

    assert (
        registry.exists("echo")
        is False
    )


def test_unregister_unknown_tool_returns_false():
    registry = ToolRegistry()

    assert (
        registry.unregister(
            "missing"
        )
        is False
    )


def test_list_registered_tools():
    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    registry.register(
        CalculatorTool()
    )

    tools = registry.list_tools()

    names = {
        tool.name
        for tool in tools
    }

    assert names == {
        "echo",
        "calculator",
    }


def test_list_names():
    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    registry.register(
        CalculatorTool()
    )

    assert set(
        registry.list_names()
    ) == {
        "echo",
        "calculator",
    }


def test_get_tool_schemas():
    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    schemas = registry.get_schemas()

    assert len(schemas) == 1

    assert (
        schemas[0]["name"]
        == "echo"
    )

    assert (
        schemas[0]["category"]
        == "utility"
    )

    assert (
        schemas[0]["parameters"][0]
        ["name"]
        == "message"
    )


def test_clear_registry():
    registry = ToolRegistry()

    registry.register(
        EchoTool()
    )

    registry.register(
        CalculatorTool()
    )

    removed = registry.clear()

    assert removed == 2
    assert registry.count() == 0
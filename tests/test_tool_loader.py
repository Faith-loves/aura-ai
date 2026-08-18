import pytest

from aura.tools.builtins.calculator import (
    CalculatorTool,
)
from aura.tools.builtins.current_time import (
    CurrentTimeTool,
)
from aura.tools.builtins.echo import EchoTool
from aura.tools.builtins.system_info import (
    SystemInfoTool,
)
from aura.tools.builtins.text_stats import (
    TextStatsTool,
)
from aura.tools.loader import ToolLoader
from aura.tools.registry import ToolRegistry


def test_loader_registers_builtin_tools():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    registered = (
        loader.load_builtin_tools()
    )

    assert registered == 5

    assert registry.exists(
        "echo"
    ) is True

    assert registry.exists(
        "system_info"
    ) is True

    assert registry.exists(
        "calculator"
    ) is True

    assert registry.exists(
        "current_time"
    ) is True

    assert registry.exists(
        "text_stats"
    ) is True


def test_loader_does_not_duplicate_tools():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    first = loader.load_builtin_tools()

    second = loader.load_builtin_tools()

    assert first == 5
    assert second == 0

    assert (
        registry.count()
        == 5
    )


def test_echo_tool_is_correct_type():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    assert isinstance(
        registry.get("echo"),
        EchoTool,
    )


def test_system_info_tool_is_correct_type():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    assert isinstance(
        registry.get(
            "system_info"
        ),
        SystemInfoTool,
    )


def test_calculator_tool_is_correct_type():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    assert isinstance(
        registry.get(
            "calculator"
        ),
        CalculatorTool,
    )


def test_current_time_tool_is_correct_type():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    assert isinstance(
        registry.get(
            "current_time"
        ),
        CurrentTimeTool,
    )


def test_text_stats_tool_is_correct_type():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    assert isinstance(
        registry.get(
            "text_stats"
        ),
        TextStatsTool,
    )


@pytest.mark.anyio
async def test_echo_builtin_executes():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    tool = registry.get(
        "echo"
    )

    result = await tool.execute(
        message="Hello AURA"
    )

    assert result.success is True

    assert (
        result.output
        == "Hello AURA"
    )


@pytest.mark.anyio
async def test_system_info_builtin_executes():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    tool = registry.get(
        "system_info"
    )

    result = await tool.execute()

    assert result.success is True

    assert isinstance(
        result.output,
        dict,
    )

    assert (
        "system"
        in result.output
    )

    assert (
        "python_version"
        in result.output
    )


@pytest.mark.anyio
async def test_calculator_builtin_executes():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    tool = registry.get(
        "calculator"
    )

    result = await tool.execute(
        operation="add",
        a=2.0,
        b=3.0,
    )

    assert result.success is True

    assert result.output == 5.0
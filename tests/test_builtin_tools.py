import pytest

from aura.tools.builtins.calculator import (
    CalculatorTool,
)
from aura.tools.builtins.current_time import (
    CurrentTimeTool,
)
from aura.tools.builtins.text_stats import (
    TextStatsTool,
)


@pytest.mark.anyio
async def test_calculator_add():
    tool = CalculatorTool()

    result = await tool.execute(
        operation="add",
        a=10.0,
        b=5.0,
    )

    assert result.success is True
    assert result.output == 15.0


@pytest.mark.anyio
async def test_calculator_subtract():
    tool = CalculatorTool()

    result = await tool.execute(
        operation="subtract",
        a=10.0,
        b=3.0,
    )

    assert result.success is True
    assert result.output == 7.0


@pytest.mark.anyio
async def test_calculator_multiply():
    tool = CalculatorTool()

    result = await tool.execute(
        operation="multiply",
        a=6.0,
        b=4.0,
    )

    assert result.success is True
    assert result.output == 24.0


@pytest.mark.anyio
async def test_calculator_divide():
    tool = CalculatorTool()

    result = await tool.execute(
        operation="divide",
        a=20.0,
        b=4.0,
    )

    assert result.success is True
    assert result.output == 5.0


@pytest.mark.anyio
async def test_calculator_rejects_division_by_zero():
    tool = CalculatorTool()

    result = await tool.execute(
        operation="divide",
        a=10.0,
        b=0.0,
    )

    assert result.success is False

    assert (
        result.error
        == "Division by zero is not allowed."
    )


@pytest.mark.anyio
async def test_current_time_tool():
    tool = CurrentTimeTool()

    result = await tool.execute()

    assert result.success is True

    assert (
        result.output["timezone"]
        == "UTC"
    )

    assert (
        "datetime"
        in result.output
    )

    assert (
        "date"
        in result.output
    )

    assert (
        "time"
        in result.output
    )


@pytest.mark.anyio
async def test_text_stats_tool():
    tool = TextStatsTool()

    result = await tool.execute(
        text="Hello AURA world"
    )

    assert result.success is True

    assert (
        result.output["characters"]
        == 16
    )

    assert (
        result.output["words"]
        == 3
    )

    assert (
        result.output[
            "characters_no_whitespace"
        ]
        == 14
    )

    assert (
        result.output["lines"]
        == 1
    )


@pytest.mark.anyio
async def test_text_stats_multiline_text():
    tool = TextStatsTool()

    result = await tool.execute(
        text=(
            "Hello AURA\n"
            "Second line"
        )
    )

    assert result.success is True

    assert (
        result.output["lines"]
        == 2
    )

    assert (
        result.output["words"]
        == 4
    )


def test_calculator_metadata():
    tool = CalculatorTool()

    assert tool.name == "calculator"

    assert (
        tool.category
        == "utility"
    )

    assert len(
        tool.parameters
    ) == 3


def test_text_stats_metadata():
    tool = TextStatsTool()

    assert (
        tool.name
        == "text_stats"
    )

    assert (
        tool.category
        == "text"
    )

    assert (
        "statistics"
        in tool.tags
    )
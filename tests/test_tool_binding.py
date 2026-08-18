import pytest

from aura.execution.binding import (
    ToolBindingManager,
)
from aura.execution.models import (
    StepExecution,
)
from aura.planning.models import (
    PlanStep,
)
from aura.tools.discovery import (
    ToolDiscovery,
)
from aura.tools.loader import ToolLoader
from aura.tools.registry import (
    ToolRegistry,
)


def create_binding_manager():
    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    discovery = ToolDiscovery(
        registry=registry
    )

    manager = ToolBindingManager(
        registry=registry,
        discovery=discovery,
    )

    return manager


def create_pair(
    title: str = "Calculate total",
):
    plan_step = PlanStep(
        title=title
    )

    step_execution = (
        StepExecution(
            plan_step_id=(
                plan_step.id
            ),
            title=(
                plan_step.title
            ),
        )
    )

    return (
        plan_step,
        step_execution,
    )


def test_bind_registered_tool():
    manager = (
        create_binding_manager()
    )

    plan_step, step_execution = (
        create_pair()
    )

    result = manager.bind(
        plan_step=plan_step,
        step_execution=step_execution,
        tool_name="calculator",
        arguments={
            "operation": "add",
            "a": 2.0,
            "b": 3.0,
        },
    )

    assert (
        result.tool_name
        == "calculator"
    )

    assert result.arguments == {
        "operation": "add",
        "a": 2.0,
        "b": 3.0,
    }

    assert (
        result.metadata[
            "tool_bound"
        ]
        is True
    )


def test_bind_unknown_tool_fails():
    manager = (
        create_binding_manager()
    )

    plan_step, step_execution = (
        create_pair()
    )

    with pytest.raises(
        ValueError,
        match="is not registered",
    ):
        manager.bind(
            plan_step=plan_step,
            step_execution=(
                step_execution
            ),
            tool_name="missing",
        )


def test_binding_requires_matching_step():
    manager = (
        create_binding_manager()
    )

    plan_step = PlanStep(
        title="Calculate"
    )

    step_execution = (
        StepExecution(
            plan_step_id=(
                "different-id"
            ),
            title="Different",
        )
    )

    with pytest.raises(
        ValueError,
        match="does not belong",
    ):
        manager.bind(
            plan_step=plan_step,
            step_execution=(
                step_execution
            ),
            tool_name="calculator",
        )


def test_unbind_tool():
    manager = (
        create_binding_manager()
    )

    plan_step, step_execution = (
        create_pair()
    )

    manager.bind(
        plan_step=plan_step,
        step_execution=step_execution,
        tool_name="calculator",
    )

    manager.unbind(
        step_execution
    )

    assert (
        step_execution.tool_name
        is None
    )

    assert (
        step_execution.arguments
        == {}
    )

    assert (
        step_execution.metadata[
            "tool_bound"
        ]
        is False
    )


def test_suggest_calculator():
    manager = (
        create_binding_manager()
    )

    plan_step = PlanStep(
        title=(
            "Calculate the total"
        )
    )

    suggestions = (
        manager.suggest_tools(
            plan_step
        )
    )

    assert (
        "calculator"
        in suggestions
    )


def test_suggest_current_time():
    manager = (
        create_binding_manager()
    )

    plan_step = PlanStep(
        title=(
            "Get current time"
        )
    )

    suggestions = (
        manager.suggest_tools(
            plan_step
        )
    )

    assert (
        "current_time"
        in suggestions
    )


def test_suggest_text_stats():
    manager = (
        create_binding_manager()
    )

    plan_step = PlanStep(
        title=(
            "Count words in text"
        )
    )

    suggestions = (
        manager.suggest_tools(
            plan_step
        )
    )

    assert (
        "text_stats"
        in suggestions
    )


def test_suggest_system_info():
    manager = (
        create_binding_manager()
    )

    plan_step = PlanStep(
        title=(
            "Inspect system environment"
        )
    )

    suggestions = (
        manager.suggest_tools(
            plan_step
        )
    )

    assert (
        "system_info"
        in suggestions
    )


def test_auto_bind_calculator():
    manager = (
        create_binding_manager()
    )

    plan_step, step_execution = (
        create_pair(
            "Calculate sum"
        )
    )

    result = manager.auto_bind(
        plan_step=plan_step,
        step_execution=step_execution,
        arguments={
            "operation": "add",
            "a": 5.0,
            "b": 7.0,
        },
    )

    assert (
        result.tool_name
        == "calculator"
    )


def test_auto_bind_without_match_fails():
    manager = (
        create_binding_manager()
    )

    plan_step, step_execution = (
        create_pair(
            "Deploy unknown quantum widget"
        )
    )

    with pytest.raises(
        ValueError,
        match="No suitable tool found",
    ):
        manager.auto_bind(
            plan_step=plan_step,
            step_execution=(
                step_execution
            ),
        )
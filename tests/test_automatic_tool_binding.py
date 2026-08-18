import pytest

from aura.execution.binding import (
    ToolBindingManager,
)
from aura.execution.manager import (
    ExecutionManager,
)
from aura.execution.models import (
    ExecutionStatus,
    StepExecutionStatus,
)
from aura.execution.runner import (
    ExecutionRunner,
)
from aura.execution.store import (
    ExecutionStore,
)
from aura.planning.models import (
    Plan,
    PlanStep,
)
from aura.planning.planner import (
    Planner,
)
from aura.tools.discovery import (
    ToolDiscovery,
)
from aura.tools.executor import (
    ToolExecutor,
)
from aura.tools.loader import (
    ToolLoader,
)
from aura.tools.registry import (
    ToolRegistry,
)
from aura.tools.validator import (
    ToolArgumentValidator,
)


def create_components():
    planner = Planner()

    store = ExecutionStore()

    execution_manager = (
        ExecutionManager(
            store=store,
            planner=planner,
        )
    )

    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    discovery = ToolDiscovery(
        registry=registry
    )

    validator = (
        ToolArgumentValidator()
    )

    executor = ToolExecutor(
        registry=registry,
        validator=validator,
    )

    binding_manager = (
        ToolBindingManager(
            registry=registry,
            discovery=discovery,
        )
    )

    runner = ExecutionRunner(
        execution_manager=(
            execution_manager
        ),
        tool_executor=executor,
        tool_binding_manager=(
            binding_manager
        ),
    )

    return (
        execution_manager,
        binding_manager,
        runner,
    )


@pytest.mark.anyio
async def test_current_time_is_automatically_bound():
    (
        execution_manager,
        _,
        runner,
    ) = create_components()

    step = PlanStep(
        title="Get current time"
    )

    plan = Plan(
        goal="Check the time",
        steps=[
            step
        ],
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    result = (
        await runner.run_execution(
            execution=execution,
            plan=plan,
        )
    )

    assert (
        result.status
        == ExecutionStatus.COMPLETED
    )

    step_execution = (
        result.step_executions[0]
    )

    assert (
        step_execution.tool_name
        == "current_time"
    )

    assert (
        step_execution.status
        == StepExecutionStatus.COMPLETED
    )

    assert (
        step_execution.output[
            "timezone"
        ]
        == "UTC"
    )


@pytest.mark.anyio
async def test_system_info_is_automatically_bound():
    (
        execution_manager,
        _,
        runner,
    ) = create_components()

    step = PlanStep(
        title=(
            "Inspect system environment"
        )
    )

    plan = Plan(
        goal="Inspect system",
        steps=[step],
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    await runner.run_execution(
        execution,
        plan,
    )

    step_execution = (
        execution.step_executions[0]
    )

    assert (
        step_execution.tool_name
        == "system_info"
    )

    assert (
        step_execution.status
        == StepExecutionStatus.COMPLETED
    )

    assert (
        "system"
        in step_execution.output
    )


@pytest.mark.anyio
async def test_text_stats_uses_metadata_arguments():
    (
        execution_manager,
        _,
        runner,
    ) = create_components()

    step = PlanStep(
        title="Count words in text",
        metadata={
            "text":
                "Hello AURA world",
        },
    )

    plan = Plan(
        goal="Analyze text",
        steps=[step],
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    await runner.run_execution(
        execution,
        plan,
    )

    step_execution = (
        execution.step_executions[0]
    )

    assert (
        step_execution.tool_name
        == "text_stats"
    )

    assert (
        step_execution.arguments
        == {
            "text":
                "Hello AURA world"
        }
    )

    assert (
        step_execution.output[
            "words"
        ]
        == 3
    )


@pytest.mark.anyio
async def test_explicit_tool_arguments_are_used():
    (
        execution_manager,
        _,
        runner,
    ) = create_components()

    step = PlanStep(
        title="Calculate total",
        metadata={
            "tool_arguments": {
                "operation": "add",
                "a": 10.0,
                "b": 15.0,
            }
        },
    )

    plan = Plan(
        goal="Calculate value",
        steps=[step],
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    await runner.run_execution(
        execution,
        plan,
    )

    step_execution = (
        execution.step_executions[0]
    )

    assert (
        step_execution.tool_name
        == "calculator"
    )

    assert (
        step_execution.output
        == 25.0
    )


@pytest.mark.anyio
async def test_existing_binding_is_preserved():
    (
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    step = PlanStep(
        title="Get current time"
    )

    plan = Plan(
        goal="Preserve binding",
        steps=[step],
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    step_execution = (
        execution.get_step_execution(
            step.id
        )
    )

    assert step_execution is not None

    binding_manager.bind(
        plan_step=step,
        step_execution=step_execution,
        tool_name="echo",
        arguments={
            "message": "Manual binding",
        },
    )

    await runner.run_execution(
        execution,
        plan,
    )

    assert (
        step_execution.tool_name
        == "echo"
    )

    assert (
        step_execution.output
        == "Manual binding"
    )


@pytest.mark.anyio
async def test_unknown_step_fails_execution_cleanly():
    (
        execution_manager,
        _,
        runner,
    ) = create_components()

    step = PlanStep(
        title=(
            "Deploy unknown quantum widget"
        )
    )

    plan = Plan(
        goal="Unknown work",
        steps=[step],
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    result = (
        await runner.run_execution(
            execution,
            plan,
        )
    )

    assert (
        result.status
        == ExecutionStatus.FAILED
    )

    assert (
        result.error_code
        == "automatic_binding_failed"
    )

    assert (
        "No suitable tool found"
        in result.error
    )
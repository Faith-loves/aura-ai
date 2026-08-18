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
    PlanStatus,
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

    execution_store = ExecutionStore()

    execution_manager = ExecutionManager(
        store=execution_store,
        planner=planner,
    )

    registry = ToolRegistry()

    loader = ToolLoader(registry=registry)

    loader.load_builtin_tools()

    discovery = ToolDiscovery(registry=registry)

    validator = ToolArgumentValidator()

    executor = ToolExecutor(
        registry=registry,
        validator=validator,
    )

    binding_manager = ToolBindingManager(
        registry=registry,
        discovery=discovery,
    )

    runner = ExecutionRunner(
        execution_manager=(execution_manager),
        tool_executor=executor,
    )

    return (
        execution_manager,
        binding_manager,
        runner,
    )


def create_three_step_plan():
    first = PlanStep(title="First calculation")

    second = PlanStep(
        title="Second calculation",
        dependencies=[first.id],
    )

    third = PlanStep(
        title="Third calculation",
        dependencies=[second.id],
    )

    return Plan(
        goal="Run three calculations",
        steps=[
            first,
            second,
            third,
        ],
    )


def bind_calculator_steps(
    binding_manager,
    execution,
    plan,
):
    arguments = [
        {
            "operation": "add",
            "a": 2.0,
            "b": 3.0,
        },
        {
            "operation": "multiply",
            "a": 4.0,
            "b": 5.0,
        },
        {
            "operation": "subtract",
            "a": 10.0,
            "b": 4.0,
        },
    ]

    for plan_step, args in zip(
        plan.steps,
        arguments,
    ):
        step_execution = execution.get_step_execution(plan_step.id)

        assert step_execution is not None

        binding_manager.bind(
            plan_step=plan_step,
            step_execution=(step_execution),
            tool_name="calculator",
            arguments=args,
        )


@pytest.mark.anyio
async def test_run_execution_completes_all_steps():
    (
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    plan = create_three_step_plan()

    execution = execution_manager.create_execution(plan)

    bind_calculator_steps(
        binding_manager,
        execution,
        plan,
    )

    result = await runner.run_execution(
        execution=execution,
        plan=plan,
    )

    assert result.status == ExecutionStatus.COMPLETED

    assert plan.status == PlanStatus.COMPLETED

    assert all(
        step.status == StepExecutionStatus.COMPLETED for step in result.step_executions
    )


@pytest.mark.anyio
async def test_autonomous_execution_outputs_are_saved():
    (
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    plan = create_three_step_plan()

    execution = execution_manager.create_execution(plan)

    bind_calculator_steps(
        binding_manager,
        execution,
        plan,
    )

    await runner.run_execution(
        execution,
        plan,
    )

    outputs = [step.output for step in execution.step_executions]

    assert outputs == [
        5.0,
        20.0,
        6.0,
    ]


@pytest.mark.anyio
async def test_execution_can_start_from_pending():
    (
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    plan = create_three_step_plan()

    execution = execution_manager.create_execution(plan)

    assert execution.status == ExecutionStatus.PENDING

    bind_calculator_steps(
        binding_manager,
        execution,
        plan,
    )

    await runner.run_execution(
        execution,
        plan,
    )

    assert execution.status == ExecutionStatus.COMPLETED


@pytest.mark.anyio
async def test_execution_stops_on_tool_failure():
    (
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    first = PlanStep(title="Broken division")

    second = PlanStep(
        title="Should not run",
        dependencies=[first.id],
    )

    plan = Plan(
        goal="Failure test",
        steps=[
            first,
            second,
        ],
    )

    execution = execution_manager.create_execution(plan)

    first_execution = execution.get_step_execution(first.id)

    second_execution = execution.get_step_execution(second.id)

    assert first_execution is not None
    assert second_execution is not None

    binding_manager.bind(
        plan_step=first,
        step_execution=first_execution,
        tool_name="calculator",
        arguments={
            "operation": "divide",
            "a": 10.0,
            "b": 0.0,
        },
    )

    binding_manager.bind(
        plan_step=second,
        step_execution=second_execution,
        tool_name="calculator",
        arguments={
            "operation": "add",
            "a": 1.0,
            "b": 1.0,
        },
    )

    await runner.run_execution(
        execution,
        plan,
    )

    assert execution.status == ExecutionStatus.FAILED

    assert first_execution.status == StepExecutionStatus.FAILED

    assert second_execution.status == StepExecutionStatus.PENDING

    assert execution.error_code == "tool_failed"


@pytest.mark.anyio
async def test_unbound_step_fails_execution_cleanly():
    (
        execution_manager,
        _,
        runner,
    ) = create_components()

    step = PlanStep(title="Unbound step")

    plan = Plan(
        goal="Unbound test",
        steps=[step],
    )

    execution = execution_manager.create_execution(plan)

    result = await runner.run_execution(
        execution=execution,
        plan=plan,
    )

    assert result.status == ExecutionStatus.FAILED

    assert result.error_code == "automatic_binding_failed"

    assert result.error == ("Step 'Unbound step' " "has no bound tool.")


@pytest.mark.anyio
async def test_completed_execution_cannot_run_again():
    (
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    plan = create_three_step_plan()

    execution = execution_manager.create_execution(plan)

    bind_calculator_steps(
        binding_manager,
        execution,
        plan,
    )

    await runner.run_execution(
        execution,
        plan,
    )

    with pytest.raises(
        ValueError,
        match=("must be pending or running"),
    ):
        await runner.run_execution(
            execution,
            plan,
        )

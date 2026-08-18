import pytest

from aura.execution.binding import (
    ToolBindingManager,
)
from aura.execution.manager import (
    ExecutionManager,
)
from aura.execution.models import (
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
    PlanStepStatus,
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

    execution_store = (
        ExecutionStore()
    )

    execution_manager = (
        ExecutionManager(
            store=execution_store,
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
    )

    return (
        planner,
        execution_manager,
        binding_manager,
        runner,
    )


def create_calculator_plan():
    step = PlanStep(
        title="Calculate total"
    )

    plan = Plan(
        goal="Calculate 5 plus 7",
        steps=[
            step
        ],
    )

    return plan


def prepare_running_bound_execution():
    (
        planner,
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    plan = (
        create_calculator_plan()
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    execution_manager.start_execution(
        execution=execution,
        plan=plan,
    )

    step_execution = (
        execution.get_step_execution(
            plan.steps[0].id
        )
    )

    assert step_execution is not None

    binding_manager.bind(
        plan_step=plan.steps[0],
        step_execution=step_execution,
        tool_name="calculator",
        arguments={
            "operation": "add",
            "a": 5.0,
            "b": 7.0,
        },
    )

    execution_manager.start_next_step(
        execution=execution,
        plan=plan,
    )

    return (
        planner,
        execution_manager,
        binding_manager,
        runner,
        plan,
        execution,
        step_execution,
    )


@pytest.mark.anyio
async def test_execute_bound_calculator():
    (
        _,
        _,
        _,
        runner,
        plan,
        execution,
        step_execution,
    ) = (
        prepare_running_bound_execution()
    )

    result = await runner.execute_current_step(
        execution=execution,
        plan=plan,
    )

    assert result.success is True

    assert result.output == 12.0

    assert (
        step_execution.status
        == StepExecutionStatus.COMPLETED
    )

    assert (
        step_execution.output
        == 12.0
    )

    assert (
        step_execution.tool_execution_id
        == result.execution_id
    )

    assert (
        execution.current_step_id
        is None
    )

    assert (
        plan.steps[0].status
        == PlanStepStatus.COMPLETED
    )


@pytest.mark.anyio
async def test_failed_bound_tool_marks_step_failed():
    (
        planner,
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    step = PlanStep(
        title="Divide numbers"
    )

    plan = Plan(
        goal="Divide by zero",
        steps=[step],
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    execution_manager.start_execution(
        execution,
        plan,
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
        tool_name="calculator",
        arguments={
            "operation": "divide",
            "a": 10.0,
            "b": 0.0,
        },
    )

    execution_manager.start_next_step(
        execution,
        plan,
    )

    result = (
        await runner.execute_current_step(
            execution,
            plan,
        )
    )

    assert result.success is False

    assert (
        step_execution.status
        == StepExecutionStatus.FAILED
    )

    assert (
        step_execution.error
        == "Division by zero is not allowed."
    )

    assert (
        step_execution.error_code
        == "tool_failed"
    )

    assert (
        step_execution.tool_execution_id
        == result.execution_id
    )

    assert (
        plan.steps[0].status
        == PlanStepStatus.FAILED
    )

    assert (
        execution.current_step_id
        is None
    )


@pytest.mark.anyio
async def test_current_step_requires_bound_tool():
    (
        _,
        execution_manager,
        _,
        runner,
    ) = create_components()

    step = PlanStep(
        title="Unbound step"
    )

    plan = Plan(
        goal="Test unbound",
        steps=[step],
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    execution_manager.start_execution(
        execution,
        plan,
    )

    execution_manager.start_next_step(
        execution,
        plan,
    )

    with pytest.raises(
        ValueError,
        match="no bound tool",
    ):
        await runner.execute_current_step(
            execution,
            plan,
        )


@pytest.mark.anyio
async def test_execution_must_be_running():
    (
        _,
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    plan = (
        create_calculator_plan()
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    step_execution = (
        execution.get_step_execution(
            plan.steps[0].id
        )
    )

    assert step_execution is not None

    binding_manager.bind(
        plan_step=plan.steps[0],
        step_execution=step_execution,
        tool_name="calculator",
        arguments={
            "operation": "add",
            "a": 1.0,
            "b": 2.0,
        },
    )

    with pytest.raises(
        ValueError,
        match="must be running",
    ):
        await runner.execute_current_step(
            execution,
            plan,
        )


@pytest.mark.anyio
async def test_requires_current_step():
    (
        _,
        execution_manager,
        _,
        runner,
    ) = create_components()

    plan = (
        create_calculator_plan()
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    execution_manager.start_execution(
        execution,
        plan,
    )

    with pytest.raises(
        ValueError,
        match="no current step",
    ):
        await runner.execute_current_step(
            execution,
            plan,
        )


@pytest.mark.anyio
async def test_start_and_execute_next_step():
    (
        _,
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    plan = (
        create_calculator_plan()
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    execution_manager.start_execution(
        execution,
        plan,
    )

    step_execution = (
        execution.get_step_execution(
            plan.steps[0].id
        )
    )

    assert step_execution is not None

    binding_manager.bind(
        plan_step=plan.steps[0],
        step_execution=step_execution,
        tool_name="calculator",
        arguments={
            "operation": "multiply",
            "a": 6.0,
            "b": 4.0,
        },
    )

    result = (
        await runner
        .start_and_execute_next_step(
            execution=execution,
            plan=plan,
        )
    )

    assert result is not None

    assert result.success is True

    assert result.output == 24.0

    assert (
        step_execution.status
        == StepExecutionStatus.COMPLETED
    )


@pytest.mark.anyio
async def test_start_and_execute_returns_none_when_finished():
    (
        _,
        execution_manager,
        binding_manager,
        runner,
    ) = create_components()

    plan = (
        create_calculator_plan()
    )

    execution = (
        execution_manager
        .create_execution(
            plan
        )
    )

    execution_manager.start_execution(
        execution,
        plan,
    )

    step_execution = (
        execution.get_step_execution(
            plan.steps[0].id
        )
    )

    assert step_execution is not None

    binding_manager.bind(
        plan_step=plan.steps[0],
        step_execution=step_execution,
        tool_name="calculator",
        arguments={
            "operation": "add",
            "a": 1.0,
            "b": 1.0,
        },
    )

    await runner.start_and_execute_next_step(
        execution,
        plan,
    )

    result = (
        await runner
        .start_and_execute_next_step(
            execution,
            plan,
        )
    )

    assert result is None
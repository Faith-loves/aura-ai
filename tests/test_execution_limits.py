import pytest

from aura.execution.binding import (
    ToolBindingManager,
)
from aura.execution.guards import (
    ExecutionGuard,
    ExecutionLimits,
)
from aura.execution.manager import (
    ExecutionManager,
)
from aura.execution.models import (
    ExecutionStatus,
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


def create_components(
    limits: ExecutionLimits,
):
    planner = Planner()

    manager = ExecutionManager(
        store=ExecutionStore(),
        planner=planner,
    )

    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    discovery = ToolDiscovery(
        registry=registry
    )

    binding_manager = (
        ToolBindingManager(
            registry=registry,
            discovery=discovery,
        )
    )

    executor = ToolExecutor(
        registry=registry
    )

    guard = ExecutionGuard(
        limits=limits
    )

    runner = ExecutionRunner(
        execution_manager=manager,
        tool_executor=executor,
        tool_binding_manager=(
            binding_manager
        ),
        execution_guard=guard,
    )

    return manager, runner


@pytest.mark.anyio
async def test_execution_fails_when_step_limit_exceeded():
    manager, runner = (
        create_components(
            ExecutionLimits(
                max_steps=1,
                max_iterations=10,
                max_failures=3,
            )
        )
    )

    first = PlanStep(
        title="Get current time"
    )

    second = PlanStep(
        title="Get current time",
        dependencies=[
            first.id
        ],
    )

    plan = Plan(
        goal="Too many steps",
        steps=[
            first,
            second,
        ],
    )

    execution = (
        manager.create_execution(
            plan
        )
    )

    result = await runner.run_execution(
        execution,
        plan,
    )

    assert (
        result.status
        == ExecutionStatus.FAILED
    )

    assert (
        result.error_code
        == "execution_limit_exceeded"
    )

    assert (
        "maximum step limit"
        in result.error
    )


@pytest.mark.anyio
async def test_execution_records_iteration_count():
    manager, runner = (
        create_components(
            ExecutionLimits(
                max_steps=10,
                max_iterations=10,
                max_failures=3,
            )
        )
    )

    step = PlanStep(
        title="Get current time"
    )

    plan = Plan(
        goal="Iteration test",
        steps=[step],
    )

    execution = (
        manager.create_execution(
            plan
        )
    )

    result = await runner.run_execution(
        execution,
        plan,
    )

    assert (
        result.status
        == ExecutionStatus.COMPLETED
    )

    assert (
        result.metadata[
            "iteration_count"
        ]
        >= 1
    )
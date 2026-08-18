import pytest

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
from aura.safety.reliability import (
    ReliabilityManager,
    ReliabilityPolicy,
)
from aura.tools.base import Tool
from aura.tools.executor import (
    ToolExecutor,
)
from aura.tools.models import (
    ToolResult,
)
from aura.tools.registry import (
    ToolRegistry,
)


class AlwaysFailsTool(Tool):
    def __init__(self):
        self.calls = 0

    @property
    def name(self) -> str:
        return "always_fails"

    @property
    def description(self) -> str:
        return "Always fails."

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        self.calls += 1

        return ToolResult(
            success=False,
            error="Permanent failure.",
            error_code="tool_failed",
        )


class AlwaysSucceedsTool(Tool):
    def __init__(self):
        self.calls = 0

    @property
    def name(self) -> str:
        return "always_succeeds"

    @property
    def description(self) -> str:
        return "Always succeeds."

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        self.calls += 1

        return ToolResult(
            success=True,
            output="ok",
        )


def create_runner(
    tool: Tool,
    failure_threshold: int = 3,
):
    planner = Planner()

    manager = ExecutionManager(
        store=ExecutionStore(),
        planner=planner,
    )

    registry = ToolRegistry()

    registry.register(
        tool
    )

    executor = ToolExecutor(
        registry=registry
    )

    reliability = (
        ReliabilityManager(
            ReliabilityPolicy(
                failure_threshold=(
                    failure_threshold
                ),
                recovery_timeout_seconds=60,
            )
        )
    )

    runner = ExecutionRunner(
        execution_manager=manager,
        tool_executor=executor,
        reliability_manager=(
            reliability
        ),
    )

    return (
        manager,
        reliability,
        runner,
    )


def create_running_execution(
    manager,
    tool_name: str,
):
    step = PlanStep(
        title="Reliability step"
    )

    plan = Plan(
        goal="Reliability test",
        steps=[step],
    )

    execution = (
        manager.create_execution(
            plan
        )
    )

    step_execution = (
        execution.get_step_execution(
            step.id
        )
    )

    assert step_execution is not None

    step_execution.tool_name = (
        tool_name
    )

    manager.start_execution(
        execution,
        plan,
    )

    manager.start_next_step(
        execution,
        plan,
    )

    return (
        plan,
        execution,
        step_execution,
    )


@pytest.mark.anyio
async def test_success_is_recorded_in_reliability():
    tool = AlwaysSucceedsTool()

    (
        manager,
        reliability,
        runner,
    ) = create_runner(
        tool
    )

    (
        plan,
        execution,
        step_execution,
    ) = create_running_execution(
        manager,
        "always_succeeds",
    )

    result = (
        await runner.execute_current_step(
            execution,
            plan,
        )
    )

    assert result.success is True

    state = reliability.get_state(
        "always_succeeds"
    )

    assert state.success_count == 1
    assert state.failure_count == 0

    assert (
        step_execution.metadata[
            "reliability_success_count"
        ]
        == 1
    )


@pytest.mark.anyio
async def test_failure_is_recorded_in_reliability():
    tool = AlwaysFailsTool()

    (
        manager,
        reliability,
        runner,
    ) = create_runner(
        tool,
        failure_threshold=3,
    )

    (
        plan,
        execution,
        step_execution,
    ) = create_running_execution(
        manager,
        "always_fails",
    )

    result = (
        await runner.execute_current_step(
            execution,
            plan,
        )
    )

    assert result.success is False

    state = reliability.get_state(
        "always_fails"
    )

    assert state.failure_count == 1

    assert (
        step_execution.metadata[
            "reliability_failure_count"
        ]
        == 1
    )


@pytest.mark.anyio
async def test_open_circuit_blocks_tool_execution():
    tool = AlwaysFailsTool()

    (
        manager,
        reliability,
        runner,
    ) = create_runner(
        tool,
        failure_threshold=1,
    )

    reliability.record_failure(
        "always_fails",
        error="Earlier failure.",
    )

    (
        plan,
        execution,
        _,
    ) = create_running_execution(
        manager,
        "always_fails",
    )

    with pytest.raises(
        RuntimeError,
        match="circuit is open",
    ):
        await runner.execute_current_step(
            execution,
            plan,
        )

    assert tool.calls == 0


@pytest.mark.anyio
async def test_run_execution_fails_when_circuit_open():
    tool = AlwaysFailsTool()

    (
        manager,
        reliability,
        runner,
    ) = create_runner(
        tool,
        failure_threshold=1,
    )

    reliability.record_failure(
        "always_fails",
        error="Earlier failure.",
    )

    step = PlanStep(
        title="Blocked reliability tool"
    )

    plan = Plan(
        goal="Circuit test",
        steps=[step],
    )

    execution = (
        manager.create_execution(
            plan
        )
    )

    step_execution = (
        execution.get_step_execution(
            step.id
        )
    )

    assert step_execution is not None

    step_execution.tool_name = (
        "always_fails"
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
        == "reliability_circuit_open"
    )

    assert tool.calls == 0


@pytest.mark.anyio
async def test_success_resets_previous_failure_state():
    tool = AlwaysSucceedsTool()

    (
        manager,
        reliability,
        runner,
    ) = create_runner(
        tool,
        failure_threshold=3,
    )

    reliability.record_failure(
        "always_succeeds",
        error="Earlier failure.",
    )

    reliability.record_failure(
        "always_succeeds",
        error="Earlier failure.",
    )

    (
        plan,
        execution,
        _,
    ) = create_running_execution(
        manager,
        "always_succeeds",
    )

    result = (
        await runner.execute_current_step(
            execution,
            plan,
        )
    )

    assert result.success is True

    state = reliability.get_state(
        "always_succeeds"
    )

    assert state.failure_count == 0

    assert state.success_count == 1

    assert (
        state.circuit_open
        is False
    )


@pytest.mark.anyio
async def test_failed_step_is_marked_failed():
    tool = AlwaysFailsTool()

    (
        manager,
        _,
        runner,
    ) = create_runner(
        tool,
        failure_threshold=3,
    )

    (
        plan,
        execution,
        step_execution,
    ) = create_running_execution(
        manager,
        "always_fails",
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
import pytest

from aura.execution.manager import (
    ExecutionManager,
)
from aura.execution.models import (
    StepExecutionStatus,
)
from aura.execution.retry import (
    RetryPolicy,
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


class FlakyTool(Tool):
    def __init__(
        self,
        failures_before_success: int,
    ):
        self.failures_before_success = (
            failures_before_success
        )

        self.attempts = 0

    @property
    def name(self) -> str:
        return "flaky"

    @property
    def description(self) -> str:
        return (
            "Fails temporarily before "
            "succeeding."
        )

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        self.attempts += 1

        if (
            self.attempts
            <= self.failures_before_success
        ):
            return ToolResult(
                success=False,
                error="Temporary failure.",
                error_code="tool_failed",
            )

        return ToolResult(
            success=True,
            output="success",
        )


class PermanentFailureTool(Tool):
    def __init__(self):
        self.attempts = 0

    @property
    def name(self) -> str:
        return "permanent_failure"

    @property
    def description(self) -> str:
        return (
            "Always fails."
        )

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        self.attempts += 1

        return ToolResult(
            success=False,
            error="Still failing.",
            error_code="tool_failed",
        )


class ValidationFailureTool(Tool):
    @property
    def name(self) -> str:
        return "validation_failure"

    @property
    def description(self) -> str:
        return "Validation test."

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=False,
            error="Bad input.",
            error_code="validation_error",
        )


def create_runner(
    tool: Tool,
    max_attempts: int = 3,
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

    runner = ExecutionRunner(
        execution_manager=manager,
        tool_executor=executor,
        retry_policy=RetryPolicy(
            max_attempts=max_attempts
        ),
    )

    return manager, runner


def create_running_bound_execution(
    manager,
    tool_name: str,
):
    step = PlanStep(
        title="Retry step"
    )

    plan = Plan(
        goal="Retry test",
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


def test_retry_policy_rejects_zero_attempts():
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        RetryPolicy(
            max_attempts=0
        )


def test_retry_policy_allows_retryable_error():
    policy = RetryPolicy(
        max_attempts=3
    )

    assert (
        policy.should_retry(
            attempt=1,
            error_code="tool_failed",
        )
        is True
    )


def test_retry_policy_stops_at_max_attempts():
    policy = RetryPolicy(
        max_attempts=3
    )

    assert (
        policy.should_retry(
            attempt=3,
            error_code="tool_failed",
        )
        is False
    )


def test_non_retryable_error_is_not_retried():
    policy = RetryPolicy(
        max_attempts=3
    )

    assert (
        policy.should_retry(
            attempt=1,
            error_code="validation_error",
        )
        is False
    )


@pytest.mark.anyio
async def test_flaky_tool_eventually_succeeds():
    tool = FlakyTool(
        failures_before_success=2
    )

    manager, runner = (
        create_runner(
            tool=tool,
            max_attempts=3,
        )
    )

    (
        plan,
        execution,
        step_execution,
    ) = create_running_bound_execution(
        manager,
        tool_name="flaky",
    )

    result = (
        await runner.execute_current_step(
            execution,
            plan,
        )
    )

    assert result.success is True

    assert tool.attempts == 3

    assert (
        step_execution.metadata[
            "attempt_count"
        ]
        == 3
    )

    assert (
        step_execution.status
        == StepExecutionStatus.COMPLETED
    )


@pytest.mark.anyio
async def test_retry_stops_after_max_attempts():
    tool = PermanentFailureTool()

    manager, runner = (
        create_runner(
            tool=tool,
            max_attempts=3,
        )
    )

    (
        plan,
        execution,
        step_execution,
    ) = create_running_bound_execution(
        manager,
        tool_name="permanent_failure",
    )

    result = (
        await runner.execute_current_step(
            execution,
            plan,
        )
    )

    assert result.success is False

    assert tool.attempts == 3

    assert (
        step_execution.metadata[
            "attempt_count"
        ]
        == 3
    )

    assert (
        step_execution.status
        == StepExecutionStatus.FAILED
    )


@pytest.mark.anyio
async def test_success_does_not_retry():
    tool = FlakyTool(
        failures_before_success=0
    )

    manager, runner = (
        create_runner(
            tool=tool,
            max_attempts=3,
        )
    )

    (
        plan,
        execution,
        step_execution,
    ) = create_running_bound_execution(
        manager,
        tool_name="flaky",
    )

    result = (
        await runner.execute_current_step(
            execution,
            plan,
        )
    )

    assert result.success is True
    assert tool.attempts == 1

    assert (
        step_execution.metadata[
            "attempt_count"
        ]
        == 1
    )


@pytest.mark.anyio
async def test_validation_failure_is_not_retried():
    tool = ValidationFailureTool()

    manager, runner = (
        create_runner(
            tool=tool,
            max_attempts=3,
        )
    )

    (
        plan,
        execution,
        step_execution,
    ) = create_running_bound_execution(
        manager,
        tool_name="validation_failure",
    )

    result = (
        await runner.execute_current_step(
            execution,
            plan,
        )
    )

    assert result.success is False

    assert (
        step_execution.metadata[
            "attempt_count"
        ]
        == 1
    )
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
from aura.safety.approvals import (
    ApprovalManager,
)
from aura.safety.authorizer import (
    ExecutionAuthorizer,
)
from aura.safety.classifier import (
    RiskClassifier,
)
from aura.safety.models import (
    ApprovalStatus,
    RiskLevel,
)
from aura.safety.permissions import (
    PermissionManager,
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


def create_components():
    planner = Planner()

    execution_manager = (
        ExecutionManager(
            store=ExecutionStore(),
            planner=planner,
        )
    )

    registry = ToolRegistry()

    loader = ToolLoader(
        registry=registry
    )

    loader.load_builtin_tools()

    executor = ToolExecutor(
        registry=registry
    )

    classifier = RiskClassifier(
        registry=registry
    )

    approvals = ApprovalManager()

    permissions = PermissionManager()

    authorizer = ExecutionAuthorizer(
        classifier=classifier,
        permission_manager=permissions,
        approval_manager=approvals,
    )

    runner = ExecutionRunner(
        execution_manager=(
            execution_manager
        ),
        tool_executor=executor,
        execution_authorizer=(
            authorizer
        ),
    )

    return (
        execution_manager,
        classifier,
        approvals,
        runner,
    )


@pytest.mark.anyio
async def test_high_risk_execution_pauses_for_approval():
    (
        manager,
        classifier,
        approvals,
        runner,
    ) = create_components()

    classifier.set_tool_risk(
        "calculator",
        RiskLevel.HIGH,
    )

    step = PlanStep(
        title="High risk calculation"
    )

    plan = Plan(
        goal="Approval test",
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
        "calculator"
    )

    step_execution.arguments = {
        "operation": "add",
        "a": 5.0,
        "b": 6.0,
    }

    result = await runner.run_execution(
        execution,
        plan,
    )

    assert (
        result.status
        == ExecutionStatus.PAUSED
    )

    assert (
        result.error_code
        == "approval_required"
    )

    assert approvals.count() == 1

    assert (
        step_execution.status
        == StepExecutionStatus.RUNNING
    )

    assert (
        "approval_id"
        in step_execution.metadata
    )


@pytest.mark.anyio
async def test_approved_action_can_resume_and_execute():
    (
        manager,
        classifier,
        approvals,
        runner,
    ) = create_components()

    classifier.set_tool_risk(
        "calculator",
        RiskLevel.HIGH,
    )

    step = PlanStep(
        title="Approved calculation"
    )

    plan = Plan(
        goal="Resume approval test",
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
        "calculator"
    )

    step_execution.arguments = {
        "operation": "add",
        "a": 10.0,
        "b": 15.0,
    }

    await runner.run_execution(
        execution,
        plan,
    )

    approval_id = (
        step_execution.metadata[
            "approval_id"
        ]
    )

    approval = approvals.approve(
        approval_id=approval_id,
        resolved_by="tester",
        reason="Approved.",
    )

    assert (
        approval.status
        == ApprovalStatus.APPROVED
    )

    runner.resume_after_approval(
        execution=execution,
        plan=plan,
    )

    assert (
        execution.status
        == ExecutionStatus.RUNNING
    )

    result = (
        await runner.execute_current_step(
            execution=execution,
            plan=plan,
        )
    )

    assert result.success is True

    assert result.output == 25.0

    assert (
        step_execution.status
        == StepExecutionStatus.COMPLETED
    )


@pytest.mark.anyio
async def test_approval_is_not_duplicated_after_resume():
    (
        manager,
        classifier,
        approvals,
        runner,
    ) = create_components()

    classifier.set_tool_risk(
        "calculator",
        RiskLevel.HIGH,
    )

    step = PlanStep(
        title="No duplicate approval"
    )

    plan = Plan(
        goal="Approval reuse",
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
        "calculator"
    )

    step_execution.arguments = {
        "operation": "multiply",
        "a": 3.0,
        "b": 4.0,
    }

    await runner.run_execution(
        execution,
        plan,
    )

    assert approvals.count() == 1

    approval_id = (
        step_execution.metadata[
            "approval_id"
        ]
    )

    approvals.approve(
        approval_id
    )

    runner.resume_after_approval(
        execution,
        plan,
    )

    await runner.execute_current_step(
        execution,
        plan,
    )

    assert approvals.count() == 1


@pytest.mark.anyio
async def test_pending_approval_cannot_resume():
    (
        manager,
        classifier,
        _,
        runner,
    ) = create_components()

    classifier.set_tool_risk(
        "calculator",
        RiskLevel.HIGH,
    )

    step = PlanStep(
        title="Pending approval"
    )

    plan = Plan(
        goal="Pending approval test",
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
        "calculator"
    )

    step_execution.arguments = {
        "operation": "add",
        "a": 1.0,
        "b": 2.0,
    }

    await runner.run_execution(
        execution,
        plan,
    )

    with pytest.raises(
        ValueError,
        match="not been approved",
    ):
        runner.resume_after_approval(
            execution,
            plan,
        )


@pytest.mark.anyio
async def test_rejected_approval_cannot_resume():
    (
        manager,
        classifier,
        approvals,
        runner,
    ) = create_components()

    classifier.set_tool_risk(
        "calculator",
        RiskLevel.HIGH,
    )

    step = PlanStep(
        title="Rejected approval"
    )

    plan = Plan(
        goal="Rejected approval test",
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
        "calculator"
    )

    step_execution.arguments = {
        "operation": "add",
        "a": 1.0,
        "b": 2.0,
    }

    await runner.run_execution(
        execution,
        plan,
    )

    approval_id = (
        step_execution.metadata[
            "approval_id"
        ]
    )

    approvals.reject(
        approval_id=approval_id,
        resolved_by="tester",
        reason="Rejected.",
    )

    with pytest.raises(
        ValueError,
        match="not been approved",
    ):
        runner.resume_after_approval(
            execution,
            plan,
        )
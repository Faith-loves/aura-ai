from aura.safety.models import (
    ApprovalStatus,
    PermissionDecision,
    RiskLevel,
    SafetyContext,
    SafetyDecision,
    SafetyPolicy,
)


def test_risk_levels():
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.MEDIUM.value == "medium"
    assert RiskLevel.HIGH.value == "high"

    assert (
        RiskLevel.CRITICAL.value
        == "critical"
    )


def test_permission_decisions():
    assert (
        PermissionDecision.ALLOW.value
        == "allow"
    )

    assert (
        PermissionDecision.DENY.value
        == "deny"
    )

    assert (
        PermissionDecision
        .REQUIRE_APPROVAL
        .value
        == "require_approval"
    )


def test_approval_statuses():
    assert (
        ApprovalStatus
        .NOT_REQUIRED
        .value
        == "not_required"
    )

    assert (
        ApprovalStatus.PENDING.value
        == "pending"
    )

    assert (
        ApprovalStatus.APPROVED.value
        == "approved"
    )

    assert (
        ApprovalStatus.REJECTED.value
        == "rejected"
    )


def test_safety_context_defaults():
    context = SafetyContext()

    assert context.tool_name is None
    assert context.action is None
    assert context.execution_id is None
    assert context.plan_id is None
    assert context.step_id is None
    assert context.arguments == {}
    assert context.metadata == {}


def test_safety_context_with_values():
    context = SafetyContext(
        tool_name="calculator",
        action="execute",
        execution_id="execution-1",
        plan_id="plan-1",
        step_id="step-1",
        arguments={
            "expression": "2 + 2"
        },
        metadata={
            "source": "test"
        },
    )

    assert (
        context.tool_name
        == "calculator"
    )

    assert (
        context.action
        == "execute"
    )

    assert (
        context.arguments[
            "expression"
        ]
        == "2 + 2"
    )


def test_safety_decision():
    context = SafetyContext(
        tool_name="calculator",
        action="execute",
    )

    decision = SafetyDecision(
        allowed=True,
        decision=(
            PermissionDecision.ALLOW
        ),
        risk_level=RiskLevel.LOW,
        reason="Low-risk action.",
        context=context,
    )

    assert decision.allowed is True

    assert (
        decision.decision
        == PermissionDecision.ALLOW
    )

    assert (
        decision.risk_level
        == RiskLevel.LOW
    )

    assert (
        decision.approval_status
        == ApprovalStatus.NOT_REQUIRED
    )

    assert decision.id
    assert decision.created_at


def test_high_risk_pending_decision():
    decision = SafetyDecision(
        allowed=False,
        decision=(
            PermissionDecision
            .REQUIRE_APPROVAL
        ),
        risk_level=RiskLevel.HIGH,
        reason=(
            "High-risk action requires "
            "approval."
        ),
        approval_status=(
            ApprovalStatus.PENDING
        ),
    )

    assert decision.allowed is False

    assert (
        decision.decision
        == PermissionDecision
        .REQUIRE_APPROVAL
    )

    assert (
        decision.approval_status
        == ApprovalStatus.PENDING
    )


def test_default_safety_policy():
    policy = SafetyPolicy()

    assert policy.name == "default"

    assert (
        policy.allow_low_risk
        is True
    )

    assert (
        policy.allow_medium_risk
        is True
    )

    assert (
        policy
        .require_approval_for_high_risk
        is True
    )

    assert (
        policy.block_critical_risk
        is True
    )


def test_custom_safety_policy():
    policy = SafetyPolicy(
        name="strict",
        allow_low_risk=True,
        allow_medium_risk=False,
        require_approval_for_high_risk=True,
        block_critical_risk=True,
        metadata={
            "environment": "production"
        },
    )

    assert policy.name == "strict"

    assert (
        policy.allow_medium_risk
        is False
    )

    assert (
        policy.metadata[
            "environment"
        ]
        == "production"
    )
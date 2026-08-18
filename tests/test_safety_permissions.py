from aura.safety.models import (
    ApprovalStatus,
    PermissionDecision,
    RiskLevel,
    SafetyContext,
    SafetyPolicy,
)
from aura.safety.permissions import (
    PermissionManager,
)


def test_low_risk_is_allowed_by_default():
    manager = PermissionManager()

    decision = manager.evaluate(
        RiskLevel.LOW
    )

    assert decision.allowed is True

    assert (
        decision.decision
        == PermissionDecision.ALLOW
    )

    assert (
        decision.approval_status
        == ApprovalStatus.NOT_REQUIRED
    )


def test_medium_risk_is_allowed_by_default():
    manager = PermissionManager()

    decision = manager.evaluate(
        RiskLevel.MEDIUM
    )

    assert decision.allowed is True

    assert (
        decision.decision
        == PermissionDecision.ALLOW
    )


def test_high_risk_requires_approval_by_default():
    manager = PermissionManager()

    decision = manager.evaluate(
        RiskLevel.HIGH
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


def test_critical_risk_is_blocked_by_default():
    manager = PermissionManager()

    decision = manager.evaluate(
        RiskLevel.CRITICAL
    )

    assert decision.allowed is False

    assert (
        decision.decision
        == PermissionDecision.DENY
    )

    assert (
        decision.risk_level
        == RiskLevel.CRITICAL
    )


def test_policy_can_disable_low_risk():
    policy = SafetyPolicy(
        allow_low_risk=False
    )

    manager = PermissionManager(
        policy=policy
    )

    decision = manager.evaluate(
        RiskLevel.LOW
    )

    assert decision.allowed is False

    assert (
        decision.decision
        == PermissionDecision.DENY
    )


def test_policy_can_disable_medium_risk():
    policy = SafetyPolicy(
        allow_medium_risk=False
    )

    manager = PermissionManager(
        policy=policy
    )

    decision = manager.evaluate(
        RiskLevel.MEDIUM
    )

    assert decision.allowed is False

    assert (
        decision.decision
        == PermissionDecision.DENY
    )


def test_policy_can_allow_high_risk_without_approval():
    policy = SafetyPolicy(
        require_approval_for_high_risk=False
    )

    manager = PermissionManager(
        policy=policy
    )

    decision = manager.evaluate(
        RiskLevel.HIGH
    )

    assert decision.allowed is True

    assert (
        decision.decision
        == PermissionDecision.ALLOW
    )

    assert (
        decision.approval_status
        == ApprovalStatus.NOT_REQUIRED
    )


def test_unblocked_critical_risk_requires_approval():
    policy = SafetyPolicy(
        block_critical_risk=False
    )

    manager = PermissionManager(
        policy=policy
    )

    decision = manager.evaluate(
        RiskLevel.CRITICAL
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


def test_context_is_preserved():
    manager = PermissionManager()

    context = SafetyContext(
        tool_name="calculator",
        action="execute",
        execution_id="execution-1",
        arguments={
            "operation": "add"
        },
    )

    decision = manager.evaluate(
        risk_level=RiskLevel.LOW,
        context=context,
    )

    assert (
        decision.context.tool_name
        == "calculator"
    )

    assert (
        decision.context.execution_id
        == "execution-1"
    )

    assert (
        decision.context.arguments[
            "operation"
        ]
        == "add"
    )


def test_custom_reason_is_preserved():
    manager = PermissionManager()

    decision = manager.evaluate(
        risk_level=RiskLevel.MEDIUM,
        reason=(
            "Allowed for controlled test."
        ),
    )

    assert (
        decision.reason
        == "Allowed for controlled test."
    )


def test_is_allowed_helper():
    manager = PermissionManager()

    assert (
        manager.is_allowed(
            RiskLevel.LOW
        )
        is True
    )

    assert (
        manager.is_allowed(
            RiskLevel.CRITICAL
        )
        is False
    )


def test_requires_approval_helper():
    manager = PermissionManager()

    assert (
        manager.requires_approval(
            RiskLevel.HIGH
        )
        is True
    )

    assert (
        manager.requires_approval(
            RiskLevel.LOW
        )
        is False
    )


def test_policy_can_be_updated():
    manager = PermissionManager()

    assert (
        manager.is_allowed(
            RiskLevel.MEDIUM
        )
        is True
    )

    manager.update_policy(
        SafetyPolicy(
            name="strict",
            allow_medium_risk=False,
        )
    )

    assert (
        manager.policy.name
        == "strict"
    )

    assert (
        manager.is_allowed(
            RiskLevel.MEDIUM
        )
        is False
    )
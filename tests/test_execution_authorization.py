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
    PermissionDecision,
    RiskLevel,
    SafetyContext,
)
from aura.safety.permissions import (
    PermissionManager,
)


def create_authorizer():
    classifier = RiskClassifier()

    permissions = PermissionManager()

    approvals = ApprovalManager()

    authorizer = ExecutionAuthorizer(
        classifier=classifier,
        permission_manager=permissions,
        approval_manager=approvals,
    )

    return (
        authorizer,
        classifier,
        approvals,
    )


def test_low_risk_action_is_authorized():
    (
        authorizer,
        _,
        approvals,
    ) = create_authorizer()

    context = SafetyContext(
        tool_name="calculator",
        action="execute",
    )

    decision = authorizer.authorize(
        context
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

    assert approvals.count() == 0


def test_medium_risk_action_is_authorized():
    (
        authorizer,
        _,
        approvals,
    ) = create_authorizer()

    context = SafetyContext(
        tool_name="system_info",
        action="system_info",
    )

    decision = authorizer.authorize(
        context
    )

    assert decision.allowed is True

    assert (
        decision.risk_level
        == RiskLevel.MEDIUM
    )

    assert approvals.count() == 0


def test_high_risk_requires_approval():
    (
        authorizer,
        classifier,
        approvals,
    ) = create_authorizer()

    classifier.set_tool_risk(
        "dangerous_tool",
        RiskLevel.HIGH,
    )

    context = SafetyContext(
        tool_name="dangerous_tool",
        action="execute",
    )

    decision = authorizer.authorize(
        context
    )

    assert decision.allowed is False

    assert (
        decision.decision
        == PermissionDecision
        .REQUIRE_APPROVAL
    )

    assert approvals.count() == 1

    assert (
        "approval_id"
        in decision.context.metadata
    )


def test_critical_action_is_denied():
    (
        authorizer,
        classifier,
        approvals,
    ) = create_authorizer()

    classifier.set_tool_risk(
        "critical_tool",
        RiskLevel.CRITICAL,
    )

    context = SafetyContext(
        tool_name="critical_tool",
        action="execute",
    )

    decision = authorizer.authorize(
        context
    )

    assert decision.allowed is False

    assert (
        decision.decision
        == PermissionDecision.DENY
    )

    assert approvals.count() == 0
import pytest

from aura.safety.approvals import (
    ApprovalManager,
)
from aura.safety.authorizer import (
    ExecutionAuthorizer,
)
from aura.safety.classifier import (
    RiskClassifier,
)
from aura.safety.enforcer import (
    SafetyEnforcer,
)
from aura.safety.models import (
    ApprovalStatus,
    RiskLevel,
    SafetyContext,
)
from aura.safety.permissions import (
    PermissionManager,
)


def create_enforcer():
    classifier = RiskClassifier()

    permissions = (
        PermissionManager()
    )

    approvals = (
        ApprovalManager()
    )

    authorizer = (
        ExecutionAuthorizer(
            classifier=classifier,
            permission_manager=permissions,
            approval_manager=approvals,
        )
    )

    enforcer = SafetyEnforcer(
        authorizer=authorizer,
        approval_manager=approvals,
    )

    return (
        classifier,
        approvals,
        enforcer,
    )


def test_low_risk_action_is_allowed():
    (
        _,
        approvals,
        enforcer,
    ) = create_enforcer()

    context = SafetyContext(
        tool_name="calculator",
        action="execute",
    )

    decision = enforcer.enforce(
        context
    )

    assert decision.allowed is True

    assert approvals.count() == 0


def test_high_risk_action_requires_approval():
    (
        classifier,
        approvals,
        enforcer,
    ) = create_enforcer()

    classifier.set_tool_risk(
        "dangerous_tool",
        RiskLevel.HIGH,
    )

    context = SafetyContext(
        tool_name="dangerous_tool",
        action="execute",
    )

    with pytest.raises(
        PermissionError,
        match="requires approval",
    ):
        enforcer.enforce(
            context
        )

    assert approvals.count() == 1


def test_critical_action_is_denied():
    (
        classifier,
        approvals,
        enforcer,
    ) = create_enforcer()

    classifier.set_tool_risk(
        "critical_tool",
        RiskLevel.CRITICAL,
    )

    context = SafetyContext(
        tool_name="critical_tool",
        action="execute",
    )

    with pytest.raises(
        PermissionError,
        match="denied",
    ):
        enforcer.enforce(
            context
        )

    assert approvals.count() == 0


def test_pending_approval_status():
    (
        classifier,
        approvals,
        enforcer,
    ) = create_enforcer()

    classifier.set_tool_risk(
        "dangerous_tool",
        RiskLevel.HIGH,
    )

    context = SafetyContext(
        tool_name="dangerous_tool",
        action="execute",
    )

    try:
        enforcer.enforce(
            context
        )

    except PermissionError:
        pass

    approval = (
        approvals.list_pending()[0]
    )

    assert (
        enforcer.is_pending(
            approval.id
        )
        is True
    )

    assert (
        enforcer.get_approval_status(
            approval.id
        )
        == ApprovalStatus.PENDING
    )


def test_approved_status():
    (
        classifier,
        approvals,
        enforcer,
    ) = create_enforcer()

    classifier.set_tool_risk(
        "dangerous_tool",
        RiskLevel.HIGH,
    )

    context = SafetyContext(
        tool_name="dangerous_tool",
        action="execute",
    )

    try:
        enforcer.enforce(
            context
        )

    except PermissionError:
        pass

    approval = (
        approvals.list_pending()[0]
    )

    approvals.approve(
        approval.id
    )

    assert (
        enforcer.is_approved(
            approval.id
        )
        is True
    )

    assert (
        enforcer.get_approval_status(
            approval.id
        )
        == ApprovalStatus.APPROVED
    )


def test_rejected_status():
    (
        classifier,
        approvals,
        enforcer,
    ) = create_enforcer()

    classifier.set_tool_risk(
        "dangerous_tool",
        RiskLevel.HIGH,
    )

    context = SafetyContext(
        tool_name="dangerous_tool",
        action="execute",
    )

    try:
        enforcer.enforce(
            context
        )

    except PermissionError:
        pass

    approval = (
        approvals.list_pending()[0]
    )

    approvals.reject(
        approval.id
    )

    assert (
        enforcer.is_rejected(
            approval.id
        )
        is True
    )

    assert (
        enforcer.get_approval_status(
            approval.id
        )
        == ApprovalStatus.REJECTED
    )


def test_unknown_approval_returns_none():
    (
        _,
        _,
        enforcer,
    ) = create_enforcer()

    assert (
        enforcer.get_approval_status(
            "missing"
        )
        is None
    )

    assert (
        enforcer.is_approved(
            "missing"
        )
        is False
    )
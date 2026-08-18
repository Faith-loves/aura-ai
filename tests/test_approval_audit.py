from aura.safety.approvals import (
    ApprovalManager,
)
from aura.safety.audit import (
    AuditEventType,
    AuditLogger,
)
from aura.safety.models import (
    ApprovalStatus,
    PermissionDecision,
    RiskLevel,
    SafetyContext,
    SafetyDecision,
)


def create_decision():
    return SafetyDecision(
        allowed=False,
        decision=(
            PermissionDecision
            .REQUIRE_APPROVAL
        ),
        risk_level=RiskLevel.HIGH,
        reason="Approval required.",
        approval_status=(
            ApprovalStatus.PENDING
        ),
        context=SafetyContext(
            tool_name="write_file",
            action="write_file",
            execution_id="execution-1",
            plan_id="plan-1",
            step_id="step-1",
        ),
    )


def test_create_approval_is_audited():
    audit = AuditLogger()

    manager = ApprovalManager(
        audit_logger=audit
    )

    manager.create_request(
        create_decision()
    )

    records = audit.list_by_event(
        AuditEventType
        .APPROVAL_CREATED
    )

    assert len(records) == 1

    assert (
        records[0].execution_id
        == "execution-1"
    )


def test_approval_is_audited():
    audit = AuditLogger()

    manager = ApprovalManager(
        audit_logger=audit
    )

    request = manager.create_request(
        create_decision()
    )

    manager.approve(
        request.id,
        resolved_by="tester",
    )

    records = audit.list_by_event(
        AuditEventType
        .APPROVAL_APPROVED
    )

    assert len(records) == 1

    assert (
        records[0].approval_id
        == request.id
    )


def test_rejection_is_audited():
    audit = AuditLogger()

    manager = ApprovalManager(
        audit_logger=audit
    )

    request = manager.create_request(
        create_decision()
    )

    manager.reject(
        request.id,
        resolved_by="tester",
        reason="Too risky.",
    )

    records = audit.list_by_event(
        AuditEventType
        .APPROVAL_REJECTED
    )

    assert len(records) == 1

    assert (
        records[0].success
        is False
    )
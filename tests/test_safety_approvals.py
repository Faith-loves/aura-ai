import pytest

from aura.safety.approvals import (
    ApprovalManager,
)
from aura.safety.models import (
    ApprovalStatus,
    PermissionDecision,
    RiskLevel,
    SafetyContext,
    SafetyDecision,
)


def create_approval_decision():
    return SafetyDecision(
        allowed=False,
        decision=(
            PermissionDecision
            .REQUIRE_APPROVAL
        ),
        risk_level=RiskLevel.HIGH,
        reason=(
            "High-risk action "
            "requires approval."
        ),
        approval_status=(
            ApprovalStatus.PENDING
        ),
        context=SafetyContext(
            tool_name="write_file",
            action="write_file",
            execution_id="execution-1",
        ),
    )


def test_create_approval_request():
    manager = ApprovalManager()

    decision = (
        create_approval_decision()
    )

    request = manager.create_request(
        decision
    )

    assert request.id

    assert (
        request.status
        == ApprovalStatus.PENDING
    )

    assert (
        request.risk_level
        == RiskLevel.HIGH
    )

    assert (
        request.safety_decision_id
        == decision.id
    )

    assert (
        request.context.tool_name
        == "write_file"
    )

    assert manager.count() == 1


def test_non_approval_decision_cannot_create_request():
    manager = ApprovalManager()

    decision = SafetyDecision(
        allowed=True,
        decision=(
            PermissionDecision.ALLOW
        ),
        risk_level=RiskLevel.LOW,
        reason="Allowed.",
    )

    with pytest.raises(
        ValueError,
        match="does not require approval",
    ):
        manager.create_request(
            decision
        )


def test_get_approval_request():
    manager = ApprovalManager()

    request = manager.create_request(
        create_approval_decision()
    )

    stored = manager.get(
        request.id
    )

    assert stored is request


def test_get_missing_returns_none():
    manager = ApprovalManager()

    assert (
        manager.get("missing")
        is None
    )


def test_get_missing_or_raise():
    manager = ApprovalManager()

    with pytest.raises(
        ValueError,
        match="was not found",
    ):
        manager.get_or_raise(
            "missing"
        )


def test_list_approval_requests():
    manager = ApprovalManager()

    manager.create_request(
        create_approval_decision()
    )

    manager.create_request(
        create_approval_decision()
    )

    requests = manager.list_all()

    assert len(requests) == 2


def test_list_pending_requests():
    manager = ApprovalManager()

    first = manager.create_request(
        create_approval_decision()
    )

    second = manager.create_request(
        create_approval_decision()
    )

    manager.approve(
        first.id
    )

    pending = manager.list_pending()

    assert pending == [
        second
    ]


def test_approve_request():
    manager = ApprovalManager()

    request = manager.create_request(
        create_approval_decision()
    )

    approved = manager.approve(
        approval_id=request.id,
        resolved_by="Faith",
        reason="Approved for test.",
    )

    assert (
        approved.status
        == ApprovalStatus.APPROVED
    )

    assert (
        approved.resolved_by
        == "Faith"
    )

    assert (
        approved.resolution_reason
        == "Approved for test."
    )

    assert (
        approved.resolved_at
        is not None
    )


def test_reject_request():
    manager = ApprovalManager()

    request = manager.create_request(
        create_approval_decision()
    )

    rejected = manager.reject(
        approval_id=request.id,
        resolved_by="Faith",
        reason="Too risky.",
    )

    assert (
        rejected.status
        == ApprovalStatus.REJECTED
    )

    assert (
        rejected.resolved_by
        == "Faith"
    )

    assert (
        rejected.resolution_reason
        == "Too risky."
    )

    assert (
        rejected.resolved_at
        is not None
    )


def test_approved_request_cannot_be_approved_again():
    manager = ApprovalManager()

    request = manager.create_request(
        create_approval_decision()
    )

    manager.approve(
        request.id
    )

    with pytest.raises(
        ValueError,
        match="Only pending",
    ):
        manager.approve(
            request.id
        )


def test_rejected_request_cannot_be_approved():
    manager = ApprovalManager()

    request = manager.create_request(
        create_approval_decision()
    )

    manager.reject(
        request.id
    )

    with pytest.raises(
        ValueError,
        match="Only pending",
    ):
        manager.approve(
            request.id
        )


def test_list_by_status():
    manager = ApprovalManager()

    approved = manager.create_request(
        create_approval_decision()
    )

    rejected = manager.create_request(
        create_approval_decision()
    )

    pending = manager.create_request(
        create_approval_decision()
    )

    manager.approve(
        approved.id
    )

    manager.reject(
        rejected.id
    )

    assert (
        manager.list_by_status(
            ApprovalStatus.APPROVED
        )
        == [approved]
    )

    assert (
        manager.list_by_status(
            ApprovalStatus.REJECTED
        )
        == [rejected]
    )

    assert (
        manager.list_by_status(
            ApprovalStatus.PENDING
        )
        == [pending]
    )


def test_delete_approval():
    manager = ApprovalManager()

    request = manager.create_request(
        create_approval_decision()
    )

    deleted = manager.delete(
        request.id
    )

    assert deleted is True
    assert manager.count() == 0


def test_delete_missing_approval():
    manager = ApprovalManager()

    assert (
        manager.delete(
            "missing"
        )
        is False
    )


def test_clear_approvals():
    manager = ApprovalManager()

    manager.create_request(
        create_approval_decision()
    )

    manager.create_request(
        create_approval_decision()
    )

    removed = manager.clear()

    assert removed == 2
    assert manager.count() == 0
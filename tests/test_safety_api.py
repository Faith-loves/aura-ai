from fastapi.testclient import (
    TestClient,
)

from apps.api.main import app
from aura.core.container import (
    container,
)
from aura.safety.models import (
    ApprovalStatus,
    PermissionDecision,
    RiskLevel,
    SafetyContext,
    SafetyDecision,
)


def clear_safety_state():
    container.approval_manager.clear()
    container.audit_logger.clear()
    container.reliability_manager.clear()


def create_pending_approval():
    decision = SafetyDecision(
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
            action="execute",
            execution_id="execution-1",
            plan_id="plan-1",
            step_id="step-1",
        ),
    )

    return (
        container.approval_manager
        .create_request(
            decision
        )
    )


def test_get_safety_policy():
    with TestClient(app) as client:
        clear_safety_state()

        response = client.get(
            "/safety/policy"
        )

        assert (
            response.status_code
            == 200
        )

        data = response.json()

        assert (
            data["name"]
            == "default"
        )

        assert (
            data["allow_low_risk"]
            is True
        )

        assert (
            data[
                "block_critical_risk"
            ]
            is True
        )


def test_list_approvals():
    with TestClient(app) as client:
        clear_safety_state()

        approval = (
            create_pending_approval()
        )

        response = client.get(
            "/safety/approvals"
        )

        assert (
            response.status_code
            == 200
        )

        data = response.json()

        assert len(data) == 1

        assert (
            data[0]["id"]
            == approval.id
        )


def test_get_approval():
    with TestClient(app) as client:
        clear_safety_state()

        approval = (
            create_pending_approval()
        )

        response = client.get(
            f"/safety/approvals/"
            f"{approval.id}"
        )

        assert (
            response.status_code
            == 200
        )

        assert (
            response.json()["status"]
            == "pending"
        )


def test_get_missing_approval():
    with TestClient(app) as client:
        clear_safety_state()

        response = client.get(
            "/safety/approvals/missing"
        )

        assert (
            response.status_code
            == 404
        )


def test_approve_request():
    with TestClient(app) as client:
        clear_safety_state()

        approval = (
            create_pending_approval()
        )

        response = client.post(
            f"/safety/approvals/"
            f"{approval.id}/approve",
            json={
                "resolved_by":
                    "tester",
                "reason":
                    "Approved.",
            },
        )

        assert (
            response.status_code
            == 200
        )

        data = response.json()

        assert (
            data["status"]
            == "approved"
        )

        assert (
            data["resolved_by"]
            == "tester"
        )


def test_reject_request():
    with TestClient(app) as client:
        clear_safety_state()

        approval = (
            create_pending_approval()
        )

        response = client.post(
            f"/safety/approvals/"
            f"{approval.id}/reject",
            json={
                "resolved_by":
                    "tester",
                "reason":
                    "Rejected.",
            },
        )

        assert (
            response.status_code
            == 200
        )

        assert (
            response.json()["status"]
            == "rejected"
        )


def test_approve_missing_request():
    with TestClient(app) as client:
        clear_safety_state()

        response = client.post(
            "/safety/approvals/"
            "missing/approve",
            json={},
        )

        assert (
            response.status_code
            == 400
        )


def test_audit_endpoint():
    with TestClient(app) as client:
        clear_safety_state()

        create_pending_approval()

        response = client.get(
            "/safety/audit"
        )

        assert (
            response.status_code
            == 200
        )

        data = response.json()

        assert len(data) == 1

        assert (
            data[0]["event_type"]
            == "approval_created"
        )


def test_reliability_endpoint():
    with TestClient(app) as client:
        clear_safety_state()

        (
            container.reliability_manager
            .record_failure(
                "calculator",
                error="Test failure.",
            )
        )

        response = client.get(
            "/safety/reliability"
        )

        assert (
            response.status_code
            == 200
        )

        data = response.json()

        assert len(data) == 1

        assert (
            data[0]["tool_name"]
            == "calculator"
        )

        assert (
            data[0]["failure_count"]
            == 1
        )


def test_reset_reliability_endpoint():
    with TestClient(app) as client:
        clear_safety_state()

        (
            container.reliability_manager
            .record_failure(
                "calculator",
                error="Failure.",
            )
        )

        response = client.post(
            "/safety/reliability/"
            "calculator/reset"
        )

        assert (
            response.status_code
            == 200
        )

        data = response.json()

        assert (
            data["tool_name"]
            == "calculator"
        )

        assert (
            data["failure_count"]
            == 0
        )

        assert (
            data["circuit_open"]
            is False
        )
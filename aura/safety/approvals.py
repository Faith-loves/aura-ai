from aura.core.logger import logger
from aura.safety.audit import (
    AuditEventType,
    AuditLogger,
)
from aura.safety.models import (
    ApprovalRequest,
    ApprovalStatus,
    PermissionDecision,
    SafetyDecision,
)


class ApprovalManager:
    def __init__(
        self,
        audit_logger: AuditLogger | None = None,
    ):
        self._requests: dict[
            str,
            ApprovalRequest,
        ] = {}

        self.audit_logger = (
            audit_logger
        )

    def create_request(
        self,
        decision: SafetyDecision,
        metadata: dict | None = None,
    ) -> ApprovalRequest:
        if (
            decision.decision
            != PermissionDecision.REQUIRE_APPROVAL
        ):
            raise ValueError(
                "Safety decision does not "
                "require approval."
            )

        request = ApprovalRequest(
            risk_level=decision.risk_level,
            reason=decision.reason,
            context=decision.context,
            safety_decision_id=decision.id,
            metadata=metadata or {},
        )

        self._requests[
            request.id
        ] = request

        logger.info(
            "Approval request created | "
            "approval_id=%s | "
            "risk=%s",
            request.id,
            request.risk_level.value,
        )

        if self.audit_logger:
            self.audit_logger.record(
                event_type=(
                    AuditEventType
                    .APPROVAL_CREATED
                ),
                message=(
                    "Approval request created."
                ),
                execution_id=(
                    request.context
                    .execution_id
                ),
                plan_id=(
                    request.context.plan_id
                ),
                step_id=(
                    request.context.step_id
                ),
                tool_name=(
                    request.context
                    .tool_name
                ),
                approval_id=request.id,
                risk_level=(
                    request.risk_level.value
                ),
                success=True,
            )

        return request

    def get(
        self,
        approval_id: str,
    ) -> ApprovalRequest | None:
        return self._requests.get(
            approval_id
        )

    def get_or_raise(
        self,
        approval_id: str,
    ) -> ApprovalRequest:
        request = self.get(
            approval_id
        )

        if request is None:
            raise ValueError(
                f"Approval request "
                f"'{approval_id}' "
                "was not found."
            )

        return request

    def list_all(
        self,
    ) -> list[ApprovalRequest]:
        return list(
            self._requests.values()
        )

    def list_pending(
        self,
    ) -> list[ApprovalRequest]:
        return [
            request
            for request
            in self._requests.values()
            if (
                request.status
                == ApprovalStatus.PENDING
            )
        ]

    def list_by_status(
        self,
        status: ApprovalStatus,
    ) -> list[ApprovalRequest]:
        return [
            request
            for request
            in self._requests.values()
            if request.status == status
        ]

    def approve(
        self,
        approval_id: str,
        resolved_by: str | None = None,
        reason: str | None = None,
    ) -> ApprovalRequest:
        request = self.get_or_raise(
            approval_id
        )

        request.approve(
            resolved_by=resolved_by,
            reason=reason,
        )

        logger.info(
            "Approval request approved | "
            "approval_id=%s | "
            "resolved_by=%s",
            approval_id,
            resolved_by,
        )

        if self.audit_logger:
            self.audit_logger.record(
                event_type=(
                    AuditEventType
                    .APPROVAL_APPROVED
                ),
                message=(
                    "Approval request approved."
                ),
                execution_id=(
                    request.context
                    .execution_id
                ),
                plan_id=(
                    request.context.plan_id
                ),
                step_id=(
                    request.context.step_id
                ),
                tool_name=(
                    request.context
                    .tool_name
                ),
                approval_id=request.id,
                risk_level=(
                    request.risk_level.value
                ),
                success=True,
                metadata={
                    "resolved_by":
                        resolved_by,
                    "reason":
                        reason,
                },
            )

        return request

    def reject(
        self,
        approval_id: str,
        resolved_by: str | None = None,
        reason: str | None = None,
    ) -> ApprovalRequest:
        request = self.get_or_raise(
            approval_id
        )

        request.reject(
            resolved_by=resolved_by,
            reason=reason,
        )

        logger.info(
            "Approval request rejected | "
            "approval_id=%s | "
            "resolved_by=%s",
            approval_id,
            resolved_by,
        )

        if self.audit_logger:
            self.audit_logger.record(
                event_type=(
                    AuditEventType
                    .APPROVAL_REJECTED
                ),
                message=(
                    "Approval request rejected."
                ),
                execution_id=(
                    request.context
                    .execution_id
                ),
                plan_id=(
                    request.context.plan_id
                ),
                step_id=(
                    request.context.step_id
                ),
                tool_name=(
                    request.context
                    .tool_name
                ),
                approval_id=request.id,
                risk_level=(
                    request.risk_level.value
                ),
                success=False,
                metadata={
                    "resolved_by":
                        resolved_by,
                    "reason":
                        reason,
                },
            )

        return request

    def delete(
        self,
        approval_id: str,
    ) -> bool:
        if (
            approval_id
            not in self._requests
        ):
            return False

        del self._requests[
            approval_id
        ]

        return True

    def clear(
        self,
    ) -> int:
        count = len(
            self._requests
        )

        self._requests.clear()

        return count

    def count(
        self,
    ) -> int:
        return len(
            self._requests
        )
from aura.core.logger import logger
from aura.safety.approvals import (
    ApprovalManager,
)
from aura.safety.audit import (
    AuditEventType,
    AuditLogger,
)
from aura.safety.authorizer import (
    ExecutionAuthorizer,
)
from aura.safety.models import (
    ApprovalStatus,
    PermissionDecision,
    SafetyContext,
    SafetyDecision,
)


class SafetyEnforcer:
    def __init__(
        self,
        authorizer: ExecutionAuthorizer,
        approval_manager: ApprovalManager,
        audit_logger: AuditLogger | None = None,
    ):
        self.authorizer = authorizer

        self.approval_manager = (
            approval_manager
        )

        self.audit_logger = (
            audit_logger
        )

    def enforce(
        self,
        context: SafetyContext,
    ) -> SafetyDecision:
        decision = (
            self.authorizer.authorize(
                context
            )
        )

        if (
            decision.decision
            == PermissionDecision.ALLOW
        ):
            if self.audit_logger:
                self.audit_logger.record(
                    event_type=(
                        AuditEventType
                        .SAFETY_ALLOWED
                    ),
                    message=(
                        "Action allowed by "
                        "safety policy."
                    ),
                    execution_id=(
                        context.execution_id
                    ),
                    plan_id=(
                        context.plan_id
                    ),
                    step_id=(
                        context.step_id
                    ),
                    tool_name=(
                        context.tool_name
                    ),
                    risk_level=(
                        decision.risk_level
                        .value
                    ),
                    success=True,
                )

            logger.info(
                "Safety enforcement allowed | "
                "risk=%s | "
                "tool=%s",
                decision.risk_level.value,
                context.tool_name,
            )

            return decision

        if (
            decision.decision
            == PermissionDecision
            .REQUIRE_APPROVAL
        ):
            approval_id = (
                decision.context
                .metadata.get(
                    "approval_id"
                )
            )

            if self.audit_logger:
                self.audit_logger.record(
                    event_type=(
                        AuditEventType
                        .APPROVAL_REQUIRED
                    ),
                    message=(
                        "Action requires "
                        "approval."
                    ),
                    execution_id=(
                        context.execution_id
                    ),
                    plan_id=(
                        context.plan_id
                    ),
                    step_id=(
                        context.step_id
                    ),
                    tool_name=(
                        context.tool_name
                    ),
                    approval_id=(
                        approval_id
                    ),
                    risk_level=(
                        decision.risk_level
                        .value
                    ),
                    success=False,
                )

            logger.warning(
                "Safety enforcement requires "
                "approval | "
                "approval_id=%s | "
                "tool=%s",
                approval_id,
                context.tool_name,
            )

            raise PermissionError(
                "Action requires approval."
            )

        if self.audit_logger:
            self.audit_logger.record(
                event_type=(
                    AuditEventType
                    .SAFETY_DENIED
                ),
                message=(
                    "Action denied by "
                    "safety policy."
                ),
                execution_id=(
                    context.execution_id
                ),
                plan_id=context.plan_id,
                step_id=context.step_id,
                tool_name=context.tool_name,
                risk_level=(
                    decision.risk_level.value
                ),
                success=False,
                error=decision.reason,
            )

        logger.warning(
            "Safety enforcement denied | "
            "tool=%s | "
            "reason=%s",
            context.tool_name,
            decision.reason,
        )

        raise PermissionError(
            "Action denied by safety policy."
        )

    def is_approved(
        self,
        approval_id: str,
    ) -> bool:
        approval = (
            self.approval_manager.get(
                approval_id
            )
        )

        if approval is None:
            return False

        return (
            approval.status
            == ApprovalStatus.APPROVED
        )

    def is_rejected(
        self,
        approval_id: str,
    ) -> bool:
        approval = (
            self.approval_manager.get(
                approval_id
            )
        )

        if approval is None:
            return False

        return (
            approval.status
            == ApprovalStatus.REJECTED
        )

    def is_pending(
        self,
        approval_id: str,
    ) -> bool:
        approval = (
            self.approval_manager.get(
                approval_id
            )
        )

        if approval is None:
            return False

        return (
            approval.status
            == ApprovalStatus.PENDING
        )

    def get_approval_status(
        self,
        approval_id: str,
    ) -> ApprovalStatus | None:
        approval = (
            self.approval_manager.get(
                approval_id
            )
        )

        if approval is None:
            return None

        return approval.status
from aura.core.logger import logger
from aura.safety.approvals import ApprovalManager
from aura.safety.classifier import RiskClassifier
from aura.safety.models import (
    ApprovalStatus,
    PermissionDecision,
    SafetyContext,
    SafetyDecision,
)
from aura.safety.permissions import PermissionManager


class ExecutionAuthorizer:
    def __init__(
        self,
        classifier: RiskClassifier,
        permission_manager: PermissionManager,
        approval_manager: ApprovalManager,
    ):
        self.classifier = classifier
        self.permission_manager = (
            permission_manager
        )
        self.approval_manager = (
            approval_manager
        )

    def authorize(
        self,
        context: SafetyContext,
    ) -> SafetyDecision:
        existing_approval_id = (
            context.metadata.get(
                "approval_id"
            )
        )

        if existing_approval_id:
            approval = (
                self.approval_manager.get(
                    existing_approval_id
                )
            )

            if approval is not None:
                if (
                    approval.status
                    == ApprovalStatus.APPROVED
                ):
                    decision = (
                        self.permission_manager
                        .evaluate(
                            risk_level=(
                                approval.risk_level
                            ),
                            context=context,
                        )
                    )

                    decision.allowed = True

                    decision.decision = (
                        PermissionDecision.ALLOW
                    )

                    decision.approval_status = (
                        ApprovalStatus.APPROVED
                    )

                    decision.reason = (
                        "Action approved by "
                        "authorization request."
                    )

                    logger.info(
                        "Execution authorization "
                        "allowed by approval | "
                        "approval_id=%s",
                        approval.id,
                    )

                    return decision

                if (
                    approval.status
                    == ApprovalStatus.REJECTED
                ):
                    decision = (
                        self.permission_manager
                        .evaluate(
                            risk_level=(
                                approval.risk_level
                            ),
                            context=context,
                        )
                    )

                    decision.allowed = False

                    decision.decision = (
                        PermissionDecision.DENY
                    )

                    decision.approval_status = (
                        ApprovalStatus.REJECTED
                    )

                    decision.reason = (
                        approval.resolution_reason
                        or "Approval request "
                        "was rejected."
                    )

                    logger.warning(
                        "Execution authorization "
                        "denied by rejected "
                        "approval | "
                        "approval_id=%s",
                        approval.id,
                    )

                    return decision

                if (
                    approval.status
                    == ApprovalStatus.PENDING
                ):
                    decision = (
                        self.permission_manager
                        .evaluate(
                            risk_level=(
                                approval.risk_level
                            ),
                            context=context,
                        )
                    )

                    decision.allowed = False

                    decision.decision = (
                        PermissionDecision
                        .REQUIRE_APPROVAL
                    )

                    decision.approval_status = (
                        ApprovalStatus.PENDING
                    )

                    decision.context.metadata[
                        "approval_id"
                    ] = approval.id

                    logger.warning(
                        "Execution authorization "
                        "still waiting for "
                        "approval | "
                        "approval_id=%s",
                        approval.id,
                    )

                    return decision

        risk_level = (
            self.classifier
            .classify_context(
                context
            )
        )

        decision = (
            self.permission_manager
            .evaluate(
                risk_level=risk_level,
                context=context,
            )
        )

        if (
            decision.decision
            == PermissionDecision
            .REQUIRE_APPROVAL
        ):
            approval = (
                self.approval_manager
                .create_request(
                    decision
                )
            )

            decision.context.metadata[
                "approval_id"
            ] = approval.id

            logger.warning(
                "Execution authorization "
                "requires approval | "
                "approval_id=%s | "
                "risk=%s",
                approval.id,
                risk_level.value,
            )

        elif (
            decision.decision
            == PermissionDecision.DENY
        ):
            logger.warning(
                "Execution authorization denied | "
                "risk=%s | reason=%s",
                risk_level.value,
                decision.reason,
            )

        else:
            logger.info(
                "Execution authorization allowed | "
                "risk=%s",
                risk_level.value,
            )

        return decision
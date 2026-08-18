from aura.core.logger import logger
from aura.safety.models import (
    ApprovalStatus,
    PermissionDecision,
    RiskLevel,
    SafetyContext,
    SafetyDecision,
    SafetyPolicy,
)


class PermissionManager:
    def __init__(
        self,
        policy: SafetyPolicy | None = None,
    ):
        self.policy = (
            policy
            or SafetyPolicy()
        )

    def evaluate(
        self,
        risk_level: RiskLevel,
        context: SafetyContext | None = None,
        reason: str | None = None,
    ) -> SafetyDecision:
        context = (
            context
            or SafetyContext()
        )

        if risk_level == RiskLevel.LOW:
            decision = (
                self._evaluate_low_risk(
                    context=context,
                    reason=reason,
                )
            )

        elif risk_level == RiskLevel.MEDIUM:
            decision = (
                self._evaluate_medium_risk(
                    context=context,
                    reason=reason,
                )
            )

        elif risk_level == RiskLevel.HIGH:
            decision = (
                self._evaluate_high_risk(
                    context=context,
                    reason=reason,
                )
            )

        elif risk_level == RiskLevel.CRITICAL:
            decision = (
                self._evaluate_critical_risk(
                    context=context,
                    reason=reason,
                )
            )

        else:
            raise ValueError(
                f"Unsupported risk level: "
                f"{risk_level}"
            )

        logger.info(
            "Permission evaluated | "
            "risk=%s | decision=%s | "
            "allowed=%s",
            risk_level.value,
            decision.decision.value,
            decision.allowed,
        )

        return decision

    def is_allowed(
        self,
        risk_level: RiskLevel,
        context: SafetyContext | None = None,
    ) -> bool:
        decision = self.evaluate(
            risk_level=risk_level,
            context=context,
        )

        return decision.allowed

    def requires_approval(
        self,
        risk_level: RiskLevel,
        context: SafetyContext | None = None,
    ) -> bool:
        decision = self.evaluate(
            risk_level=risk_level,
            context=context,
        )

        return (
            decision.decision
            == PermissionDecision.REQUIRE_APPROVAL
        )

    def update_policy(
        self,
        policy: SafetyPolicy,
    ) -> None:
        self.policy = policy

        logger.info(
            "Safety policy updated | "
            "policy=%s",
            policy.name,
        )

    def _evaluate_low_risk(
        self,
        context: SafetyContext,
        reason: str | None,
    ) -> SafetyDecision:
        if self.policy.allow_low_risk:
            return SafetyDecision(
                allowed=True,
                decision=(
                    PermissionDecision.ALLOW
                ),
                risk_level=RiskLevel.LOW,
                reason=(
                    reason
                    or "Low-risk action allowed."
                ),
                approval_status=(
                    ApprovalStatus.NOT_REQUIRED
                ),
                context=context,
            )

        return SafetyDecision(
            allowed=False,
            decision=(
                PermissionDecision.DENY
            ),
            risk_level=RiskLevel.LOW,
            reason=(
                reason
                or "Low-risk actions are "
                "disabled by policy."
            ),
            approval_status=(
                ApprovalStatus.NOT_REQUIRED
            ),
            context=context,
        )

    def _evaluate_medium_risk(
        self,
        context: SafetyContext,
        reason: str | None,
    ) -> SafetyDecision:
        if self.policy.allow_medium_risk:
            return SafetyDecision(
                allowed=True,
                decision=(
                    PermissionDecision.ALLOW
                ),
                risk_level=(
                    RiskLevel.MEDIUM
                ),
                reason=(
                    reason
                    or "Medium-risk action "
                    "allowed."
                ),
                approval_status=(
                    ApprovalStatus.NOT_REQUIRED
                ),
                context=context,
            )

        return SafetyDecision(
            allowed=False,
            decision=(
                PermissionDecision.DENY
            ),
            risk_level=RiskLevel.MEDIUM,
            reason=(
                reason
                or "Medium-risk actions are "
                "disabled by policy."
            ),
            approval_status=(
                ApprovalStatus.NOT_REQUIRED
            ),
            context=context,
        )

    def _evaluate_high_risk(
        self,
        context: SafetyContext,
        reason: str | None,
    ) -> SafetyDecision:
        if (
            self.policy
            .require_approval_for_high_risk
        ):
            return SafetyDecision(
                allowed=False,
                decision=(
                    PermissionDecision
                    .REQUIRE_APPROVAL
                ),
                risk_level=RiskLevel.HIGH,
                reason=(
                    reason
                    or "High-risk action "
                    "requires approval."
                ),
                approval_status=(
                    ApprovalStatus.PENDING
                ),
                context=context,
            )

        return SafetyDecision(
            allowed=True,
            decision=(
                PermissionDecision.ALLOW
            ),
            risk_level=RiskLevel.HIGH,
            reason=(
                reason
                or "High-risk action allowed "
                "by policy."
            ),
            approval_status=(
                ApprovalStatus.NOT_REQUIRED
            ),
            context=context,
        )

    def _evaluate_critical_risk(
        self,
        context: SafetyContext,
        reason: str | None,
    ) -> SafetyDecision:
        if (
            self.policy
            .block_critical_risk
        ):
            return SafetyDecision(
                allowed=False,
                decision=(
                    PermissionDecision.DENY
                ),
                risk_level=(
                    RiskLevel.CRITICAL
                ),
                reason=(
                    reason
                    or "Critical-risk action "
                    "blocked by policy."
                ),
                approval_status=(
                    ApprovalStatus.NOT_REQUIRED
                ),
                context=context,
            )

        return SafetyDecision(
            allowed=False,
            decision=(
                PermissionDecision
                .REQUIRE_APPROVAL
            ),
            risk_level=RiskLevel.CRITICAL,
            reason=(
                reason
                or "Critical-risk action "
                "requires explicit approval."
            ),
            approval_status=(
                ApprovalStatus.PENDING
            ),
            context=context,
        )
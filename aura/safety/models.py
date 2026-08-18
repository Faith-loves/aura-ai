from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PermissionDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class ApprovalStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SafetyContext(BaseModel):
    tool_name: str | None = None

    action: str | None = None

    execution_id: str | None = None

    plan_id: str | None = None

    step_id: str | None = None

    arguments: dict[str, Any] = Field(
        default_factory=dict
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class SafetyDecision(BaseModel):
    id: str = Field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    allowed: bool

    decision: PermissionDecision

    risk_level: RiskLevel

    reason: str

    approval_status: ApprovalStatus = (
        ApprovalStatus.NOT_REQUIRED
    )

    context: SafetyContext = Field(
        default_factory=SafetyContext
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC
        )
    )


class SafetyPolicy(BaseModel):
    name: str = "default"

    allow_low_risk: bool = True

    allow_medium_risk: bool = True

    require_approval_for_high_risk: bool = (
        True
    )

    block_critical_risk: bool = True

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ApprovalRequest(BaseModel):
    id: str = Field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    status: ApprovalStatus = (
        ApprovalStatus.PENDING
    )

    risk_level: RiskLevel

    reason: str

    context: SafetyContext = Field(
        default_factory=SafetyContext
    )

    safety_decision_id: str | None = None

    requested_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC
        )
    )

    resolved_at: datetime | None = None

    resolved_by: str | None = None

    resolution_reason: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    def approve(
        self,
        resolved_by: str | None = None,
        reason: str | None = None,
    ) -> None:
        if self.status != ApprovalStatus.PENDING:
            raise ValueError(
                "Only pending approval requests "
                "can be approved."
            )

        self.status = ApprovalStatus.APPROVED
        self.resolved_at = datetime.now(UTC)
        self.resolved_by = resolved_by
        self.resolution_reason = reason

    def reject(
        self,
        resolved_by: str | None = None,
        reason: str | None = None,
    ) -> None:
        if self.status != ApprovalStatus.PENDING:
            raise ValueError(
                "Only pending approval requests "
                "can be rejected."
            )

        self.status = ApprovalStatus.REJECTED
        self.resolved_at = datetime.now(UTC)
        self.resolved_by = resolved_by
        self.resolution_reason = reason
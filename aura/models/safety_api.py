from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from aura.safety.audit import (
    AuditEventType,
)
from aura.safety.models import (
    ApprovalStatus,
    RiskLevel,
)


class ApprovalDecisionRequest(BaseModel):
    resolved_by: str | None = None

    reason: str | None = None


class SafetyPolicyResponse(BaseModel):
    name: str

    allow_low_risk: bool

    allow_medium_risk: bool

    require_approval_for_high_risk: bool

    block_critical_risk: bool

    metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )


class ApprovalResponse(BaseModel):
    id: str

    status: ApprovalStatus

    risk_level: RiskLevel

    reason: str

    safety_decision_id: str | None = None

    tool_name: str | None = None

    execution_id: str | None = None

    plan_id: str | None = None

    step_id: str | None = None

    requested_at: datetime

    resolved_at: datetime | None = None

    resolved_by: str | None = None

    resolution_reason: str | None = None

    metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )


class AuditResponse(BaseModel):
    id: str

    event_type: AuditEventType

    message: str

    execution_id: str | None = None

    plan_id: str | None = None

    step_id: str | None = None

    tool_name: str | None = None

    approval_id: str | None = None

    risk_level: str | None = None

    success: bool | None = None

    error: str | None = None

    metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )

    created_at: datetime


class ReliabilityStateResponse(BaseModel):
    tool_name: str

    failure_count: int

    success_count: int

    circuit_open: bool

    opened_at: datetime | None = None

    last_failure_at: datetime | None = None

    last_success_at: datetime | None = None

    last_error: str | None = None

    metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )
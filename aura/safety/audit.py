from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from aura.core.logger import logger


class AuditEventType(str, Enum):
    SAFETY_ALLOWED = "safety_allowed"
    SAFETY_DENIED = "safety_denied"

    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_CREATED = "approval_created"
    APPROVAL_APPROVED = "approval_approved"
    APPROVAL_REJECTED = "approval_rejected"

    TOOL_EXECUTION_STARTED = (
        "tool_execution_started"
    )

    TOOL_EXECUTION_SUCCEEDED = (
        "tool_execution_succeeded"
    )

    TOOL_EXECUTION_FAILED = (
        "tool_execution_failed"
    )

    EXECUTION_PAUSED = "execution_paused"

    EXECUTION_RESUMED = (
        "execution_resumed"
    )

    EXECUTION_FAILED = (
        "execution_failed"
    )


class AuditRecord(BaseModel):
    id: str = Field(
        default_factory=lambda: str(
            uuid4()
        )
    )

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

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC
        )
    )


class AuditLogger:
    def __init__(self):
        self._records: list[
            AuditRecord
        ] = []

    def record(
        self,
        event_type: AuditEventType,
        message: str,
        execution_id: str | None = None,
        plan_id: str | None = None,
        step_id: str | None = None,
        tool_name: str | None = None,
        approval_id: str | None = None,
        risk_level: str | None = None,
        success: bool | None = None,
        error: str | None = None,
        metadata: dict[
            str,
            Any,
        ] | None = None,
    ) -> AuditRecord:
        record = AuditRecord(
            event_type=event_type,
            message=message,
            execution_id=execution_id,
            plan_id=plan_id,
            step_id=step_id,
            tool_name=tool_name,
            approval_id=approval_id,
            risk_level=risk_level,
            success=success,
            error=error,
            metadata=metadata or {},
        )

        self._records.append(
            record
        )

        logger.info(
            "Audit event | "
            "event=%s | "
            "execution_id=%s | "
            "tool=%s",
            event_type.value,
            execution_id,
            tool_name,
        )

        return record

    def list_all(
        self,
    ) -> list[AuditRecord]:
        return list(
            self._records
        )

    def get(
        self,
        record_id: str,
    ) -> AuditRecord | None:
        for record in self._records:
            if record.id == record_id:
                return record

        return None

    def list_by_event(
        self,
        event_type: AuditEventType,
    ) -> list[AuditRecord]:
        return [
            record
            for record
            in self._records
            if (
                record.event_type
                == event_type
            )
        ]

    def list_by_execution(
        self,
        execution_id: str,
    ) -> list[AuditRecord]:
        return [
            record
            for record
            in self._records
            if (
                record.execution_id
                == execution_id
            )
        ]

    def list_by_tool(
        self,
        tool_name: str,
    ) -> list[AuditRecord]:
        return [
            record
            for record
            in self._records
            if (
                record.tool_name
                == tool_name
            )
        ]

    def clear(
        self,
    ) -> int:
        count = len(
            self._records
        )

        self._records.clear()

        return count

    def count(
        self,
    ) -> int:
        return len(
            self._records
        )
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class PlanStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PlanStepStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStep(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    title: str = Field(
        ...,
        min_length=1,
    )

    description: str = ""

    status: PlanStepStatus = (
        PlanStepStatus.PENDING
    )

    priority: int = Field(
        default=3,
        ge=1,
        le=5,
    )

    dependencies: list[str] = Field(
        default_factory=list
    )

    metadata: dict = Field(
        default_factory=dict
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    def change_status(
        self,
        new_status: PlanStepStatus,
    ) -> None:
        from aura.planning.transitions import (
            validate_step_transition,
        )

        validate_step_transition(
            self.status,
            new_status,
        )

        self.status = new_status
        self.updated_at = datetime.now(UTC)


class Plan(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    goal: str = Field(
        ...,
        min_length=1,
    )

    status: PlanStatus = (
        PlanStatus.PENDING
    )

    steps: list[PlanStep] = Field(
        default_factory=list
    )

    metadata: dict = Field(
        default_factory=dict
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    def change_status(
        self,
        new_status: PlanStatus,
    ) -> None:
        from aura.planning.transitions import (
            validate_plan_transition,
        )

        validate_plan_transition(
            self.status,
            new_status,
        )

        self.status = new_status
        self.updated_at = datetime.now(UTC)
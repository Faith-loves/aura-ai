from pydantic import BaseModel, Field

from aura.planning.models import (
    PlanStatus,
    PlanStepStatus,
)


class CreatePlanRequest(BaseModel):
    goal: str = Field(
        ...,
        min_length=1,
    )

    metadata: dict = Field(
        default_factory=dict
    )


class UpdateStepPriorityRequest(BaseModel):
    priority: int = Field(
        ...,
        ge=1,
        le=5,
    )


class PlanStepResponse(BaseModel):
    id: str
    title: str
    description: str
    status: PlanStepStatus
    priority: int
    dependencies: list[str]
    metadata: dict


class PlanResponse(BaseModel):
    id: str
    goal: str
    status: PlanStatus
    steps: list[PlanStepResponse]
    metadata: dict
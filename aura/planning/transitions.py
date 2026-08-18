from aura.planning.models import (
    PlanStatus,
    PlanStepStatus,
)


PLAN_TRANSITIONS: dict[
    PlanStatus,
    set[PlanStatus],
] = {
    PlanStatus.PENDING: {
        PlanStatus.IN_PROGRESS,
        PlanStatus.FAILED,
        PlanStatus.CANCELLED,
    },
    PlanStatus.IN_PROGRESS: {
        PlanStatus.COMPLETED,
        PlanStatus.FAILED,
        PlanStatus.CANCELLED,
    },
    PlanStatus.COMPLETED: set(),
    PlanStatus.FAILED: set(),
    PlanStatus.CANCELLED: set(),
}


STEP_TRANSITIONS: dict[
    PlanStepStatus,
    set[PlanStepStatus],
] = {
    PlanStepStatus.PENDING: {
        PlanStepStatus.READY,
        PlanStepStatus.SKIPPED,
    },
    PlanStepStatus.READY: {
        PlanStepStatus.IN_PROGRESS,
        PlanStepStatus.SKIPPED,
    },
    PlanStepStatus.IN_PROGRESS: {
        PlanStepStatus.COMPLETED,
        PlanStepStatus.FAILED,
        PlanStepStatus.SKIPPED,
    },
    PlanStepStatus.COMPLETED: set(),
    PlanStepStatus.FAILED: set(),
    PlanStepStatus.SKIPPED: set(),
}


def can_transition_plan(
    current: PlanStatus,
    new: PlanStatus,
) -> bool:
    return new in PLAN_TRANSITIONS.get(
        current,
        set(),
    )


def can_transition_step(
    current: PlanStepStatus,
    new: PlanStepStatus,
) -> bool:
    return new in STEP_TRANSITIONS.get(
        current,
        set(),
    )


def validate_plan_transition(
    current: PlanStatus,
    new: PlanStatus,
) -> None:
    if current == new:
        return

    if not can_transition_plan(
        current,
        new,
    ):
        raise ValueError(
            f"Invalid plan status transition: "
            f"{current.value} -> {new.value}"
        )


def validate_step_transition(
    current: PlanStepStatus,
    new: PlanStepStatus,
) -> None:
    if current == new:
        return

    if not can_transition_step(
        current,
        new,
    ):
        raise ValueError(
            f"Invalid plan step status transition: "
            f"{current.value} -> {new.value}"
        )
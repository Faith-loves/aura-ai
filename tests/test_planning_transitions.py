import pytest

from aura.planning.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from aura.planning.transitions import (
    can_transition_plan,
    can_transition_step,
)


def test_plan_can_move_from_pending_to_in_progress():
    assert can_transition_plan(
        PlanStatus.PENDING,
        PlanStatus.IN_PROGRESS,
    ) is True


def test_plan_cannot_move_from_completed_to_pending():
    assert can_transition_plan(
        PlanStatus.COMPLETED,
        PlanStatus.PENDING,
    ) is False


def test_plan_change_status():
    plan = Plan(
        goal="Build AURA planner."
    )

    plan.change_status(
        PlanStatus.IN_PROGRESS
    )

    assert (
        plan.status
        == PlanStatus.IN_PROGRESS
    )


def test_invalid_plan_status_change_raises_error():
    plan = Plan(
        goal="Build AURA planner.",
        status=PlanStatus.COMPLETED,
    )

    with pytest.raises(
        ValueError,
        match="Invalid plan status transition",
    ):
        plan.change_status(
            PlanStatus.PENDING
        )


def test_step_can_move_from_pending_to_ready():
    assert can_transition_step(
        PlanStepStatus.PENDING,
        PlanStepStatus.READY,
    ) is True


def test_step_change_status():
    step = PlanStep(
        title="Analyze goal"
    )

    step.change_status(
        PlanStepStatus.READY
    )

    assert (
        step.status
        == PlanStepStatus.READY
    )


def test_step_can_complete_valid_sequence():
    step = PlanStep(
        title="Build API"
    )

    step.change_status(
        PlanStepStatus.READY
    )

    step.change_status(
        PlanStepStatus.IN_PROGRESS
    )

    step.change_status(
        PlanStepStatus.COMPLETED
    )

    assert (
        step.status
        == PlanStepStatus.COMPLETED
    )


def test_completed_step_cannot_restart():
    step = PlanStep(
        title="Finished task",
        status=PlanStepStatus.COMPLETED,
    )

    with pytest.raises(
        ValueError,
        match="Invalid plan step status transition",
    ):
        step.change_status(
            PlanStepStatus.READY
        )


def test_same_plan_status_is_allowed():
    plan = Plan(
        goal="Test goal"
    )

    plan.change_status(
        PlanStatus.PENDING
    )

    assert (
        plan.status
        == PlanStatus.PENDING
    )


def test_same_step_status_is_allowed():
    step = PlanStep(
        title="Test step"
    )

    step.change_status(
        PlanStepStatus.PENDING
    )

    assert (
        step.status
        == PlanStepStatus.PENDING
    )
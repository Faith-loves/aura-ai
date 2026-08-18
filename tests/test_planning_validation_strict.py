import pytest

from aura.planning.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from aura.planning.planner import Planner
from aura.planning.validator import PlanValidator


def test_generated_plan_passes_strict_validation():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a REST API."
    )

    planner.validate_plan(
        plan
    )


def test_empty_plan_is_invalid():
    validator = PlanValidator()

    plan = Plan(
        goal="Empty plan"
    )

    with pytest.raises(
        ValueError,
        match="at least one step",
    ):
        validator.validate(
            plan
        )


def test_duplicate_step_ids_are_invalid():
    validator = PlanValidator()

    first = PlanStep(
        title="First"
    )

    second = PlanStep(
        id=first.id,
        title="Second",
    )

    plan = Plan(
        goal="Duplicate IDs",
        steps=[
            first,
            second,
        ],
    )

    with pytest.raises(
        ValueError,
        match="duplicate step IDs",
    ):
        validator.validate(
            plan
        )


def test_duplicate_dependencies_are_invalid():
    validator = PlanValidator()

    first = PlanStep(
        title="First"
    )

    second = PlanStep(
        title="Second",
        dependencies=[
            first.id,
            first.id,
        ],
    )

    plan = Plan(
        goal="Duplicate dependencies",
        steps=[
            first,
            second,
        ],
    )

    with pytest.raises(
        ValueError,
        match="duplicate dependencies",
    ):
        validator.validate(
            plan
        )


def test_unknown_dependency_is_invalid():
    validator = PlanValidator()

    step = PlanStep(
        title="Broken dependency",
        dependencies=[
            "unknown-step"
        ],
    )

    plan = Plan(
        goal="Unknown dependency",
        steps=[
            step
        ],
    )

    with pytest.raises(
        ValueError,
        match="unknown step",
    ):
        validator.validate(
            plan
        )


def test_self_dependency_is_invalid():
    validator = PlanValidator()

    step = PlanStep(
        title="Self dependency"
    )

    step.dependencies = [
        step.id
    ]

    plan = Plan(
        goal="Self dependency",
        steps=[
            step
        ],
    )

    with pytest.raises(
        ValueError,
        match="cannot depend on itself",
    ):
        validator.validate(
            plan
        )


def test_circular_dependency_is_invalid():
    validator = PlanValidator()

    first = PlanStep(
        title="First"
    )

    second = PlanStep(
        title="Second"
    )

    first.dependencies = [
        second.id
    ]

    second.dependencies = [
        first.id
    ]

    plan = Plan(
        goal="Circular plan",
        steps=[
            first,
            second,
        ],
    )

    with pytest.raises(
        ValueError,
        match="circular dependency",
    ):
        validator.validate(
            plan
        )


def test_ready_step_requires_completed_dependencies():
    validator = PlanValidator()

    first = PlanStep(
        title="First",
        status=PlanStepStatus.PENDING,
    )

    second = PlanStep(
        title="Second",
        status=PlanStepStatus.READY,
        dependencies=[
            first.id
        ],
    )

    plan = Plan(
        goal="Invalid readiness",
        status=PlanStatus.IN_PROGRESS,
        steps=[
            first,
            second,
        ],
    )

    with pytest.raises(
        ValueError,
        match="incomplete dependencies",
    ):
        validator.validate(
            plan
        )


def test_in_progress_step_requires_completed_dependencies():
    validator = PlanValidator()

    first = PlanStep(
        title="First",
        status=PlanStepStatus.READY,
    )

    second = PlanStep(
        title="Second",
        status=PlanStepStatus.IN_PROGRESS,
        dependencies=[
            first.id
        ],
    )

    plan = Plan(
        goal="Invalid execution",
        status=PlanStatus.IN_PROGRESS,
        steps=[
            first,
            second,
        ],
    )

    with pytest.raises(
        ValueError,
        match="incomplete dependencies",
    ):
        validator.validate(
            plan
        )


def test_completed_plan_cannot_have_pending_steps():
    validator = PlanValidator()

    first = PlanStep(
        title="Finished",
        status=PlanStepStatus.COMPLETED,
    )

    second = PlanStep(
        title="Not finished",
        status=PlanStepStatus.PENDING,
        dependencies=[
            first.id
        ],
    )

    plan = Plan(
        goal="Incomplete completed plan",
        status=PlanStatus.COMPLETED,
        steps=[
            first,
            second,
        ],
    )

    with pytest.raises(
        ValueError,
        match="unfinished steps",
    ):
        validator.validate(
            plan
        )


def test_pending_plan_cannot_have_ready_steps():
    validator = PlanValidator()

    step = PlanStep(
        title="Already ready",
        status=PlanStepStatus.READY,
    )

    plan = Plan(
        goal="Invalid pending plan",
        status=PlanStatus.PENDING,
        steps=[
            step
        ],
    )

    with pytest.raises(
        ValueError,
        match="already started",
    ):
        validator.validate(
            plan
        )


def test_valid_in_progress_plan():
    validator = PlanValidator()

    first = PlanStep(
        title="First",
        status=PlanStepStatus.COMPLETED,
    )

    second = PlanStep(
        title="Second",
        status=PlanStepStatus.READY,
        dependencies=[
            first.id
        ],
    )

    plan = Plan(
        goal="Valid active plan",
        status=PlanStatus.IN_PROGRESS,
        steps=[
            first,
            second,
        ],
    )

    validator.validate(
        plan
    )


def test_valid_completed_plan():
    validator = PlanValidator()

    first = PlanStep(
        title="First",
        status=PlanStepStatus.COMPLETED,
    )

    second = PlanStep(
        title="Second",
        status=PlanStepStatus.COMPLETED,
        dependencies=[
            first.id
        ],
    )

    plan = Plan(
        goal="Finished plan",
        status=PlanStatus.COMPLETED,
        steps=[
            first,
            second,
        ],
    )

    validator.validate(
        plan
    )


def test_skipped_steps_allowed_in_completed_plan():
    validator = PlanValidator()

    first = PlanStep(
        title="Required",
        status=PlanStepStatus.COMPLETED,
    )

    second = PlanStep(
        title="Optional",
        status=PlanStepStatus.SKIPPED,
        dependencies=[
            first.id
        ],
    )

    plan = Plan(
        goal="Completed with skipped step",
        status=PlanStatus.COMPLETED,
        steps=[
            first,
            second,
        ],
    )

    validator.validate(
        plan
    )
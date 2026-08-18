import pytest

from aura.planning.models import (
    Plan,
    PlanStep,
)
from aura.planning.planner import Planner
from aura.planning.validator import PlanValidator


def test_valid_plan_passes_validation():
    validator = PlanValidator()

    first = PlanStep(
        title="First"
    )

    second = PlanStep(
        title="Second",
        dependencies=[
            first.id
        ],
    )

    plan = Plan(
        goal="Valid plan",
        steps=[
            first,
            second,
        ],
    )

    validator.validate(
        plan
    )


def test_unknown_dependency_fails_validation():
    validator = PlanValidator()

    step = PlanStep(
        title="Broken step",
        dependencies=[
            "missing-step-id"
        ],
    )

    plan = Plan(
        goal="Broken plan",
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


def test_self_dependency_fails_validation():
    validator = PlanValidator()

    step = PlanStep(
        title="Self dependent"
    )

    step.dependencies = [
        step.id
    ]

    plan = Plan(
        goal="Invalid plan",
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


def test_direct_cycle_fails_validation():
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


def test_indirect_cycle_fails_validation():
    validator = PlanValidator()

    first = PlanStep(
        title="First"
    )

    second = PlanStep(
        title="Second"
    )

    third = PlanStep(
        title="Third"
    )

    first.dependencies = [
        third.id
    ]

    second.dependencies = [
        first.id
    ]

    third.dependencies = [
        second.id
    ]

    plan = Plan(
        goal="Indirect circular plan",
        steps=[
            first,
            second,
            third,
        ],
    )

    with pytest.raises(
        ValueError,
        match="circular dependency",
    ):
        validator.validate(
            plan
        )


def test_generated_plan_is_valid():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a REST API."
    )

    planner.validate_plan(
        plan
    )
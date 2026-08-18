import pytest

from aura.planning.models import (
    PlanStatus,
    PlanStepStatus,
)
from aura.planning.planner import Planner


def test_create_plan():
    planner = Planner()

    plan = planner.create_plan(
        goal="Build a REST API."
    )

    assert plan.goal == "Build a REST API."
    assert plan.status == PlanStatus.PENDING
    assert plan.steps == []


def test_create_step():
    planner = Planner()

    step = planner.create_step(
        title="Design API",
        description="Design the API structure.",
        priority=4,
    )

    assert step.title == "Design API"
    assert step.priority == 4
    assert step.status == PlanStepStatus.PENDING


def test_add_step_to_plan():
    planner = Planner()

    plan = planner.create_plan(
        "Build an API."
    )

    step = planner.create_step(
        "Design API"
    )

    planner.add_step(
        plan,
        step,
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].id == step.id


def test_duplicate_step_cannot_be_added():
    planner = Planner()

    plan = planner.create_plan(
        "Build an API."
    )

    step = planner.create_step(
        "Design API"
    )

    planner.add_step(
        plan,
        step,
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        planner.add_step(
            plan,
            step,
        )


def test_start_plan_marks_first_step_ready():
    planner = Planner()

    plan = planner.create_plan(
        "Build an API."
    )

    first = planner.create_step(
        "Design API"
    )

    second = planner.create_step(
        "Implement API",
        dependencies=[
            first.id
        ],
    )

    planner.add_step(
        plan,
        first,
    )

    planner.add_step(
        plan,
        second,
    )

    planner.start_plan(
        plan
    )

    assert (
        plan.status
        == PlanStatus.IN_PROGRESS
    )

    assert (
        first.status
        == PlanStepStatus.READY
    )

    assert (
        second.status
        == PlanStepStatus.PENDING
    )


def test_complete_step_unlocks_dependency():
    planner = Planner()

    plan = planner.create_plan(
        "Build an API."
    )

    first = planner.create_step(
        "Design API"
    )

    second = planner.create_step(
        "Implement API",
        dependencies=[
            first.id
        ],
    )

    planner.add_step(
        plan,
        first,
    )

    planner.add_step(
        plan,
        second,
    )

    planner.start_plan(
        plan
    )

    planner.start_step(
        plan,
        first.id,
    )

    planner.complete_step(
        plan,
        first.id,
    )

    assert (
        first.status
        == PlanStepStatus.COMPLETED
    )

    assert (
        second.status
        == PlanStepStatus.READY
    )


def test_get_next_step_uses_priority():
    planner = Planner()

    plan = planner.create_plan(
        "Build an application."
    )

    low_priority = planner.create_step(
        title="Low priority",
        priority=1,
    )

    high_priority = planner.create_step(
        title="High priority",
        priority=5,
    )

    planner.add_step(
        plan,
        low_priority,
    )

    planner.add_step(
        plan,
        high_priority,
    )

    planner.start_plan(
        plan
    )

    next_step = planner.get_next_step(
        plan
    )

    assert next_step is not None
    assert next_step.id == high_priority.id


def test_complete_plan_requires_finished_steps():
    planner = Planner()

    plan = planner.create_plan(
        "Build an API."
    )

    step = planner.create_step(
        "Build API"
    )

    planner.add_step(
        plan,
        step,
    )

    planner.start_plan(
        plan
    )

    with pytest.raises(
        ValueError,
        match="unfinished steps",
    ):
        planner.complete_plan(
            plan
        )


def test_complete_plan():
    planner = Planner()

    plan = planner.create_plan(
        "Build an API."
    )

    step = planner.create_step(
        "Build API"
    )

    planner.add_step(
        plan,
        step,
    )

    planner.start_plan(
        plan
    )

    planner.start_step(
        plan,
        step.id,
    )

    planner.complete_step(
        plan,
        step.id,
    )

    planner.complete_plan(
        plan
    )

    assert (
        plan.status
        == PlanStatus.COMPLETED
    )


def test_remove_step():
    planner = Planner()

    plan = planner.create_plan(
        "Build an API."
    )

    step = planner.create_step(
        "Design API"
    )

    planner.add_step(
        plan,
        step,
    )

    planner.remove_step(
        plan,
        step.id,
    )

    assert plan.steps == []


def test_cannot_remove_step_with_dependents():
    planner = Planner()

    plan = planner.create_plan(
        "Build an API."
    )

    first = planner.create_step(
        "Design API"
    )

    second = planner.create_step(
        "Implement API",
        dependencies=[
            first.id
        ],
    )

    planner.add_step(
        plan,
        first,
    )

    planner.add_step(
        plan,
        second,
    )

    with pytest.raises(
        ValueError,
        match="depend on it",
    ):
        planner.remove_step(
            plan,
            first.id,
        )
import pytest

from aura.planning.models import PlanStatus
from aura.planning.planner import Planner


def test_generate_software_plan():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a Python REST API for managing tasks."
    )

    assert plan.goal == (
        "Build a Python REST API for managing tasks."
    )

    assert plan.status == PlanStatus.PENDING

    assert len(plan.steps) == 6

    titles = [
        step.title
        for step in plan.steps
    ]

    assert titles == [
        "Define API requirements",
        "Design data models",
        "Design API endpoints",
        "Implement API",
        "Test API",
        "Document and finalize API",
    ]


def test_generated_software_plan_has_dependencies():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a web application."
    )

    assert len(plan.steps) == 5

    assert plan.steps[0].dependencies == []

    assert plan.steps[1].dependencies == [
        plan.steps[0].id
    ]

    assert plan.steps[2].dependencies == [
        plan.steps[1].id
    ]

    assert plan.steps[3].dependencies == [
        plan.steps[2].id
    ]

    assert plan.steps[4].dependencies == [
        plan.steps[3].id
    ]


def test_generate_research_plan():
    planner = Planner()

    plan = planner.generate_plan(
        "Research the benefits of FastAPI."
    )

    assert len(plan.steps) == 4

    titles = [
        step.title
        for step in plan.steps
    ]

    assert titles == [
        "Define research objective",
        "Gather information",
        "Analyze findings",
        "Form conclusion",
    ]


def test_generate_writing_plan():
    planner = Planner()

    plan = planner.generate_plan(
        "Write a technical report about AURA."
    )

    assert len(plan.steps) == 4

    titles = [
        step.title
        for step in plan.steps
    ]

    assert titles == [
        "Understand writing requirements",
        "Create outline",
        "Draft content",
        "Review and refine",
    ]


def test_generate_general_plan():
    planner = Planner()

    plan = planner.generate_plan(
        "Organize my workspace."
    )

    assert len(plan.steps) == 4

    titles = [
        step.title
        for step in plan.steps
    ]

    assert titles == [
        "Understand goal",
        "Prepare approach",
        "Execute approach",
        "Verify outcome",
    ]


def test_generate_plan_preserves_metadata():
    planner = Planner()

    plan = planner.generate_plan(
        goal="Build an API.",
        metadata={
            "source": "test",
        },
    )

    assert plan.metadata == {
        "source": "test",
    }


def test_generate_plan_rejects_empty_goal():
    planner = Planner()

    with pytest.raises(
        ValueError,
        match="Goal cannot be empty",
    ):
        planner.generate_plan(
            "   "
        )


def test_generated_steps_have_categories():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a mobile app."
    )

    for step in plan.steps:
        assert "category" in step.metadata


def test_generated_plan_can_be_started():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a REST API."
    )

    planner.start_plan(
        plan
    )

    assert (
        plan.status
        == PlanStatus.IN_PROGRESS
    )

    assert (
        plan.steps[0].status.value
        == "ready"
    )

    for step in plan.steps[1:]:
        assert (
            step.status.value
            == "pending"
        )


def test_generated_plan_has_unique_step_ids():
    planner = Planner()

    plan = planner.generate_plan(
        "Build a web application."
    )

    step_ids = [
        step.id
        for step in plan.steps
    ]

    assert len(step_ids) == len(
        set(step_ids)
    )
from aura.planning.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)


def test_plan_step_creation():
    step = PlanStep(
        title="Understand requirements",
        description="Analyze the user's goal.",
    )

    assert step.id is not None
    assert step.title == (
        "Understand requirements"
    )
    assert step.status == (
        PlanStepStatus.PENDING
    )
    assert step.priority == 3
    assert step.dependencies == []
    assert step.metadata == {}


def test_plan_creation():
    plan = Plan(
        goal="Build a REST API."
    )

    assert plan.id is not None
    assert plan.goal == (
        "Build a REST API."
    )
    assert plan.status == (
        PlanStatus.PENDING
    )
    assert plan.steps == []
    assert plan.metadata == {}


def test_plan_with_steps():
    first_step = PlanStep(
        title="Design API"
    )

    second_step = PlanStep(
        title="Build API",
        dependencies=[
            first_step.id
        ],
    )

    plan = Plan(
        goal="Build an API.",
        steps=[
            first_step,
            second_step,
        ],
    )

    assert len(plan.steps) == 2

    assert (
        plan.steps[1].dependencies
        == [first_step.id]
    )


def test_all_plan_statuses_exist():
    assert PlanStatus.PENDING.value == (
        "pending"
    )

    assert (
        PlanStatus.IN_PROGRESS.value
        == "in_progress"
    )

    assert PlanStatus.COMPLETED.value == (
        "completed"
    )

    assert PlanStatus.FAILED.value == (
        "failed"
    )

    assert PlanStatus.CANCELLED.value == (
        "cancelled"
    )


def test_all_plan_step_statuses_exist():
    assert (
        PlanStepStatus.PENDING.value
        == "pending"
    )

    assert (
        PlanStepStatus.READY.value
        == "ready"
    )

    assert (
        PlanStepStatus.IN_PROGRESS.value
        == "in_progress"
    )

    assert (
        PlanStepStatus.COMPLETED.value
        == "completed"
    )

    assert (
        PlanStepStatus.FAILED.value
        == "failed"
    )

    assert (
        PlanStepStatus.SKIPPED.value
        == "skipped"
    )
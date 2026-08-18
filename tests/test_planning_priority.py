import pytest

from aura.planning.models import (
    PlanStepStatus,
)
from aura.planning.planner import Planner
from aura.planning.priority import PriorityManager


def test_priority_manager_accepts_valid_priority():
    manager = PriorityManager()

    manager.validate_priority(1)
    manager.validate_priority(3)
    manager.validate_priority(5)


def test_priority_below_one_is_rejected():
    manager = PriorityManager()

    with pytest.raises(
        ValueError,
        match="lower than 1",
    ):
        manager.validate_priority(0)


def test_priority_above_five_is_rejected():
    manager = PriorityManager()

    with pytest.raises(
        ValueError,
        match="higher than 5",
    ):
        manager.validate_priority(6)


def test_ready_steps_sorted_by_priority():
    planner = Planner()

    plan = planner.create_plan(
        "Priority test"
    )

    low = planner.create_step(
        title="Low priority",
        priority=1,
    )

    medium = planner.create_step(
        title="Medium priority",
        priority=3,
    )

    high = planner.create_step(
        title="High priority",
        priority=5,
    )

    planner.add_step(plan, low)
    planner.add_step(plan, medium)
    planner.add_step(plan, high)

    planner.start_plan(plan)

    ready = planner.get_ready_steps(
        plan
    )

    assert [
        step.title
        for step in ready
    ] == [
        "High priority",
        "Medium priority",
        "Low priority",
    ]


def test_next_step_selects_highest_priority():
    planner = Planner()

    plan = planner.create_plan(
        "Next step test"
    )

    low = planner.create_step(
        title="Low priority",
        priority=1,
    )

    high = planner.create_step(
        title="High priority",
        priority=5,
    )

    planner.add_step(plan, low)
    planner.add_step(plan, high)

    planner.start_plan(plan)

    next_step = planner.get_next_step(
        plan
    )

    assert next_step is not None
    assert next_step.id == high.id


def test_priority_can_be_changed():
    planner = Planner()

    plan = planner.create_plan(
        "Priority update test"
    )

    step = planner.create_step(
        title="Change me",
        priority=2,
    )

    planner.add_step(
        plan,
        step,
    )

    updated = planner.set_step_priority(
        plan=plan,
        step_id=step.id,
        priority=5,
    )

    assert updated.priority == 5


def test_priority_change_affects_next_step():
    planner = Planner()

    plan = planner.create_plan(
        "Dynamic priority test"
    )

    first = planner.create_step(
        title="First",
        priority=5,
    )

    second = planner.create_step(
        title="Second",
        priority=2,
    )

    planner.add_step(plan, first)
    planner.add_step(plan, second)

    planner.start_plan(plan)

    assert (
        planner.get_next_step(plan).id
        == first.id
    )

    planner.set_step_priority(
        plan=plan,
        step_id=second.id,
        priority=5,
    )

    planner.set_step_priority(
        plan=plan,
        step_id=first.id,
        priority=1,
    )

    assert (
        planner.get_next_step(plan).id
        == second.id
    )


def test_missing_step_priority_update_fails():
    planner = Planner()

    plan = planner.create_plan(
        "Missing step test"
    )

    with pytest.raises(
        ValueError,
        match="was not found",
    ):
        planner.set_step_priority(
            plan=plan,
            step_id="missing-id",
            priority=5,
        )


def test_blocked_high_priority_step_is_not_selected():
    planner = Planner()

    plan = planner.create_plan(
        "Dependency priority test"
    )

    first = planner.create_step(
        title="Required first",
        priority=2,
    )

    blocked = planner.create_step(
        title="Blocked high priority",
        priority=5,
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
        blocked,
    )

    planner.start_plan(
        plan
    )

    assert (
        first.status
        == PlanStepStatus.READY
    )

    assert (
        blocked.status
        == PlanStepStatus.PENDING
    )

    next_step = planner.get_next_step(
        plan
    )

    assert next_step is not None
    assert next_step.id == first.id


def test_no_ready_steps_returns_none():
    planner = Planner()

    plan = planner.create_plan(
        "No ready steps"
    )

    assert (
        planner.get_next_step(plan)
        is None
    )
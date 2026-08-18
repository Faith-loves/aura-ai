import pytest

from aura.safety.reliability import (
    ReliabilityManager,
    ReliabilityPolicy,
)


def test_policy_rejects_zero_failure_threshold():
    with pytest.raises(
        ValueError,
        match="failure_threshold",
    ):
        ReliabilityPolicy(
            failure_threshold=0
        )


def test_policy_rejects_negative_timeout():
    with pytest.raises(
        ValueError,
        match="recovery_timeout_seconds",
    ):
        ReliabilityPolicy(
            recovery_timeout_seconds=-1
        )


def test_new_tool_can_execute():
    manager = ReliabilityManager()

    assert (
        manager.can_execute(
            "calculator"
        )
        is True
    )


def test_failure_is_recorded():
    manager = ReliabilityManager(
        ReliabilityPolicy(
            failure_threshold=3
        )
    )

    state = manager.record_failure(
        "calculator",
        error="Failure.",
    )

    assert state.failure_count == 1

    assert (
        state.last_error
        == "Failure."
    )

    assert (
        state.circuit_open
        is False
    )


def test_circuit_opens_after_threshold():
    manager = ReliabilityManager(
        ReliabilityPolicy(
            failure_threshold=3
        )
    )

    manager.record_failure(
        "calculator"
    )

    manager.record_failure(
        "calculator"
    )

    state = manager.record_failure(
        "calculator"
    )

    assert state.failure_count == 3

    assert (
        state.circuit_open
        is True
    )

    assert (
        state.opened_at
        is not None
    )


def test_open_circuit_blocks_execution():
    manager = ReliabilityManager(
        ReliabilityPolicy(
            failure_threshold=1,
            recovery_timeout_seconds=60,
        )
    )

    manager.record_failure(
        "calculator"
    )

    assert (
        manager.can_execute(
            "calculator"
        )
        is False
    )


def test_success_resets_failures():
    manager = ReliabilityManager(
        ReliabilityPolicy(
            failure_threshold=3
        )
    )

    manager.record_failure(
        "calculator"
    )

    manager.record_failure(
        "calculator"
    )

    state = manager.record_success(
        "calculator"
    )

    assert state.failure_count == 0

    assert state.success_count == 1

    assert (
        state.circuit_open
        is False
    )

    assert state.last_error is None


def test_manual_reset():
    manager = ReliabilityManager(
        ReliabilityPolicy(
            failure_threshold=1
        )
    )

    manager.record_failure(
        "calculator"
    )

    assert (
        manager.can_execute(
            "calculator"
        )
        is False
    )

    state = manager.reset_tool(
        "calculator"
    )

    assert state.failure_count == 0

    assert (
        state.circuit_open
        is False
    )


def test_zero_timeout_recovers_immediately():
    manager = ReliabilityManager(
        ReliabilityPolicy(
            failure_threshold=1,
            recovery_timeout_seconds=0,
        )
    )

    manager.record_failure(
        "calculator"
    )

    assert (
        manager.can_execute(
            "calculator"
        )
        is True
    )


def test_list_unhealthy_tools():
    manager = ReliabilityManager(
        ReliabilityPolicy(
            failure_threshold=1,
            recovery_timeout_seconds=60,
        )
    )

    manager.record_failure(
        "calculator"
    )

    manager.record_success(
        "echo"
    )

    unhealthy = (
        manager.list_unhealthy()
    )

    assert len(unhealthy) == 1

    assert (
        unhealthy[0].tool_name
        == "calculator"
    )


def test_clear_reliability_state():
    manager = ReliabilityManager()

    manager.record_success(
        "calculator"
    )

    manager.record_success(
        "echo"
    )

    assert manager.count() == 2

    removed = manager.clear()

    assert removed == 2

    assert manager.count() == 0
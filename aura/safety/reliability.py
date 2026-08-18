from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from aura.core.logger import logger


@dataclass
class ToolHealthState:
    tool_name: str

    failure_count: int = 0

    success_count: int = 0

    circuit_open: bool = False

    opened_at: datetime | None = None

    last_failure_at: datetime | None = None

    last_success_at: datetime | None = None

    last_error: str | None = None

    metadata: dict = field(
        default_factory=dict
    )


@dataclass
class ReliabilityPolicy:
    failure_threshold: int = 3

    recovery_timeout_seconds: int = 60

    def __post_init__(
        self,
    ) -> None:
        if self.failure_threshold < 1:
            raise ValueError(
                "failure_threshold must be "
                "at least 1."
            )

        if (
            self.recovery_timeout_seconds
            < 0
        ):
            raise ValueError(
                "recovery_timeout_seconds "
                "cannot be negative."
            )


class ReliabilityManager:
    def __init__(
        self,
        policy: ReliabilityPolicy | None = None,
    ):
        self.policy = (
            policy
            or ReliabilityPolicy()
        )

        self._tools: dict[
            str,
            ToolHealthState,
        ] = {}

    def get_state(
        self,
        tool_name: str,
    ) -> ToolHealthState:
        normalized = (
            tool_name.strip().lower()
        )

        if not normalized:
            raise ValueError(
                "tool_name cannot be empty."
            )

        if normalized not in self._tools:
            self._tools[
                normalized
            ] = ToolHealthState(
                tool_name=normalized
            )

        return self._tools[
            normalized
        ]

    def can_execute(
        self,
        tool_name: str,
    ) -> bool:
        state = self.get_state(
            tool_name
        )

        if not state.circuit_open:
            return True

        if self._recovery_timeout_elapsed(
            state
        ):
            logger.info(
                "Tool circuit recovery "
                "timeout elapsed | "
                "tool=%s",
                tool_name,
            )

            self.reset_tool(
                tool_name
            )

            return True

        return False

    def record_success(
        self,
        tool_name: str,
    ) -> ToolHealthState:
        state = self.get_state(
            tool_name
        )

        state.success_count += 1

        state.failure_count = 0

        state.last_success_at = (
            datetime.now(UTC)
        )

        state.last_error = None

        if state.circuit_open:
            state.circuit_open = False
            state.opened_at = None

        logger.info(
            "Tool success recorded | "
            "tool=%s | "
            "success_count=%s",
            tool_name,
            state.success_count,
        )

        return state

    def record_failure(
        self,
        tool_name: str,
        error: str | None = None,
    ) -> ToolHealthState:
        state = self.get_state(
            tool_name
        )

        state.failure_count += 1

        state.last_failure_at = (
            datetime.now(UTC)
        )

        state.last_error = error

        if (
            state.failure_count
            >= self.policy.failure_threshold
        ):
            state.circuit_open = True

            if state.opened_at is None:
                state.opened_at = (
                    datetime.now(UTC)
                )

            logger.warning(
                "Tool circuit opened | "
                "tool=%s | failures=%s",
                tool_name,
                state.failure_count,
            )

        else:
            logger.warning(
                "Tool failure recorded | "
                "tool=%s | failures=%s",
                tool_name,
                state.failure_count,
            )

        return state

    def reset_tool(
        self,
        tool_name: str,
    ) -> ToolHealthState:
        state = self.get_state(
            tool_name
        )

        state.failure_count = 0

        state.circuit_open = False

        state.opened_at = None

        state.last_error = None

        logger.info(
            "Tool reliability state reset | "
            "tool=%s",
            tool_name,
        )

        return state

    def list_states(
        self,
    ) -> list[ToolHealthState]:
        return list(
            self._tools.values()
        )

    def list_unhealthy(
        self,
    ) -> list[ToolHealthState]:
        return [
            state
            for state
            in self._tools.values()
            if state.circuit_open
        ]

    def clear(
        self,
    ) -> int:
        count = len(
            self._tools
        )

        self._tools.clear()

        return count

    def count(
        self,
    ) -> int:
        return len(
            self._tools
        )

    def _recovery_timeout_elapsed(
        self,
        state: ToolHealthState,
    ) -> bool:
        if state.opened_at is None:
            return False

        recovery_time = (
            state.opened_at
            + timedelta(
                seconds=(
                    self.policy
                    .recovery_timeout_seconds
                )
            )
        )

        return (
            datetime.now(UTC)
            >= recovery_time
        )
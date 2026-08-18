from aura.execution.models import (
    Execution,
    ExecutionStatus,
)


class ExecutionStore:
    def __init__(self):
        self._executions: dict[
            str,
            Execution,
        ] = {}

    def save(
        self,
        execution: Execution,
    ) -> Execution:
        self._executions[
            execution.id
        ] = execution

        return execution

    def get(
        self,
        execution_id: str,
    ) -> Execution | None:
        return self._executions.get(
            execution_id
        )

    def exists(
        self,
        execution_id: str,
    ) -> bool:
        return (
            execution_id
            in self._executions
        )

    def list_all(
        self,
    ) -> list[Execution]:
        return list(
            self._executions.values()
        )

    def list_by_status(
        self,
        status: ExecutionStatus,
    ) -> list[Execution]:
        return [
            execution
            for execution
            in self._executions.values()
            if execution.status
            == status
        ]

    def delete(
        self,
        execution_id: str,
    ) -> bool:
        if (
            execution_id
            not in self._executions
        ):
            return False

        del self._executions[
            execution_id
        ]

        return True

    def clear(
        self,
    ) -> int:
        count = len(
            self._executions
        )

        self._executions.clear()

        return count

    def count(
        self,
    ) -> int:
        return len(
            self._executions
        )
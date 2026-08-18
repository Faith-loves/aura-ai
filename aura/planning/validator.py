from aura.planning.models import (
    Plan,
    PlanStatus,
    PlanStepStatus,
)


class PlanValidator:
    def validate(
        self,
        plan: Plan,
    ) -> None:
        self._validate_goal(
            plan
        )

        self._validate_has_steps(
            plan
        )

        self._validate_unique_step_ids(
            plan
        )

        self._validate_duplicate_dependencies(
            plan
        )

        self._validate_dependencies_exist(
            plan
        )

        self._validate_no_self_dependencies(
            plan
        )

        self._validate_no_cycles(
            plan
        )

        self._validate_step_states(
            plan
        )

        self._validate_plan_state(
            plan
        )

    def _validate_goal(
        self,
        plan: Plan,
    ) -> None:
        if not plan.goal.strip():
            raise ValueError(
                "Plan goal cannot be empty."
            )

    def _validate_has_steps(
        self,
        plan: Plan,
    ) -> None:
        if not plan.steps:
            raise ValueError(
                "Plan must contain at least one step."
            )

    def _validate_unique_step_ids(
        self,
        plan: Plan,
    ) -> None:
        step_ids = [
            step.id
            for step in plan.steps
        ]

        if len(step_ids) != len(
            set(step_ids)
        ):
            raise ValueError(
                "Plan contains duplicate step IDs."
            )

    def _validate_duplicate_dependencies(
        self,
        plan: Plan,
    ) -> None:
        for step in plan.steps:
            if len(
                step.dependencies
            ) != len(
                set(step.dependencies)
            ):
                raise ValueError(
                    f"Step '{step.id}' contains "
                    "duplicate dependencies."
                )

    def _validate_dependencies_exist(
        self,
        plan: Plan,
    ) -> None:
        valid_ids = {
            step.id
            for step in plan.steps
        }

        for step in plan.steps:
            for dependency_id in step.dependencies:
                if dependency_id not in valid_ids:
                    raise ValueError(
                        f"Step '{step.id}' depends on "
                        f"unknown step '{dependency_id}'."
                    )

    def _validate_no_self_dependencies(
        self,
        plan: Plan,
    ) -> None:
        for step in plan.steps:
            if step.id in step.dependencies:
                raise ValueError(
                    f"Step '{step.id}' cannot "
                    "depend on itself."
                )

    def _validate_no_cycles(
        self,
        plan: Plan,
    ) -> None:
        graph = {
            step.id: list(
                step.dependencies
            )
            for step in plan.steps
        }

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(
            step_id: str,
        ) -> None:
            if step_id in visited:
                return

            if step_id in visiting:
                raise ValueError(
                    "Plan contains a "
                    "circular dependency."
                )

            visiting.add(
                step_id
            )

            for dependency_id in graph[
                step_id
            ]:
                visit(
                    dependency_id
                )

            visiting.remove(
                step_id
            )

            visited.add(
                step_id
            )

        for step_id in graph:
            visit(
                step_id
            )

    def _validate_step_states(
        self,
        plan: Plan,
    ) -> None:
        step_map = {
            step.id: step
            for step in plan.steps
        }

        execution_states = {
            PlanStepStatus.READY,
            PlanStepStatus.IN_PROGRESS,
            PlanStepStatus.COMPLETED,
            PlanStepStatus.FAILED,
        }

        for step in plan.steps:
            if (
                step.status
                not in execution_states
            ):
                continue

            incomplete_dependencies = [
                dependency_id
                for dependency_id
                in step.dependencies
                if (
                    step_map[
                        dependency_id
                    ].status
                    != PlanStepStatus.COMPLETED
                )
            ]

            if incomplete_dependencies:
                raise ValueError(
                    f"Step '{step.id}' is "
                    f"'{step.status.value}' but "
                    "has incomplete dependencies."
                )

    def _validate_plan_state(
        self,
        plan: Plan,
    ) -> None:
        if (
            plan.status
            == PlanStatus.PENDING
        ):
            invalid_steps = [
                step
                for step in plan.steps
                if step.status
                not in {
                    PlanStepStatus.PENDING,
                }
            ]

            if invalid_steps:
                raise ValueError(
                    "Pending plan contains "
                    "steps that have already started."
                )

        if (
            plan.status
            == PlanStatus.COMPLETED
        ):
            unfinished_steps = [
                step
                for step in plan.steps
                if step.status
                not in {
                    PlanStepStatus.COMPLETED,
                    PlanStepStatus.SKIPPED,
                }
            ]

            if unfinished_steps:
                raise ValueError(
                    "Completed plan contains "
                    "unfinished steps."
                )

        if (
            plan.status
            == PlanStatus.IN_PROGRESS
        ):
            active_or_finished = [
                step
                for step in plan.steps
                if step.status
                in {
                    PlanStepStatus.READY,
                    PlanStepStatus.IN_PROGRESS,
                    PlanStepStatus.COMPLETED,
                    PlanStepStatus.FAILED,
                    PlanStepStatus.SKIPPED,
                }
            ]

            if not active_or_finished:
                raise ValueError(
                    "In-progress plan has no "
                    "active or processed steps."
                )
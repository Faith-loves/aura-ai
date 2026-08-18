from aura.planning.models import PlanStep


class PriorityManager:
    MIN_PRIORITY = 1
    MAX_PRIORITY = 5

    def validate_priority(
        self,
        priority: int,
    ) -> None:
        if priority < self.MIN_PRIORITY:
            raise ValueError(
                "Priority cannot be lower than 1."
            )

        if priority > self.MAX_PRIORITY:
            raise ValueError(
                "Priority cannot be higher than 5."
            )

    def sort_steps(
        self,
        steps: list[PlanStep],
    ) -> list[PlanStep]:
        return sorted(
            steps,
            key=lambda step: (
                -step.priority,
                step.created_at,
                step.id,
            ),
        )

    def select_next(
        self,
        steps: list[PlanStep],
    ) -> PlanStep | None:
        if not steps:
            return None

        sorted_steps = self.sort_steps(
            steps
        )

        return sorted_steps[0]
from aura.planning.models import Plan


class PlanStore:
    def __init__(self):
        self._plans: dict[
            str,
            Plan,
        ] = {}

    def save(
        self,
        plan: Plan,
    ) -> Plan:
        self._plans[
            plan.id
        ] = plan

        return plan

    def get(
        self,
        plan_id: str,
    ) -> Plan | None:
        return self._plans.get(
            plan_id
        )

    def exists(
        self,
        plan_id: str,
    ) -> bool:
        return (
            plan_id
            in self._plans
        )

    def list_all(
        self,
    ) -> list[Plan]:
        return list(
            self._plans.values()
        )

    def delete(
        self,
        plan_id: str,
    ) -> bool:
        if plan_id not in self._plans:
            return False

        del self._plans[
            plan_id
        ]

        return True

    def clear(
        self,
    ) -> int:
        count = len(
            self._plans
        )

        self._plans.clear()

        return count

    def count(
        self,
    ) -> int:
        return len(
            self._plans
        )
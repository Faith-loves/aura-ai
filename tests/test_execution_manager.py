from aura.core.logger import logger
from aura.execution.models import (
    Execution,
    ExecutionStatus,
    StepExecution,
    StepExecutionStatus,
)
from aura.execution.store import ExecutionStore
from aura.planning.models import (
    Plan,
    PlanStatus,
    PlanStep,
    PlanStepStatus,
)
from aura.planning.planner import Planner


class ExecutionManager:
    def __init__(
        self,
        store: ExecutionStore,
        planner: Planner | None = None,
    ):
        self.store = store
        self.planner = planner or Planner()

    def create_execution(
        self,
        plan: Plan,
        metadata: dict | None = None,
    ) -> Execution:
        if not plan.steps:
            raise ValueError(
                "Cannot create an execution "
                "for a plan with no steps."
            )

        execution = Execution(
            plan_id=plan.id,
            goal=plan.goal,
            metadata=metadata or {},
        )

        for plan_step in plan.steps:
            step_execution = StepExecution(
                plan_step_id=plan_step.id,
                title=plan_step.title,
                status=self._map_step_status(
                    plan_step.status
                ),
                metadata={
                    "plan_step_metadata": dict(
                        plan_step.metadata
                    ),
                    "priority": plan_step.priority,
                    "dependencies": list(
                        plan_step.dependencies
                    ),
                },
            )

            execution.add_step_execution(
                step_execution
            )

        self.store.save(
            execution
        )

        logger.info(
            "Created execution | "
            "execution_id=%s | "
            "plan_id=%s | steps=%s",
            execution.id,
            plan.id,
            len(
                execution.step_executions
            ),
        )

        return execution

    def get_execution(
        self,
        execution_id: str,
    ) -> Execution:
        execution = self.store.get(
            execution_id
        )

        if execution is None:
            raise ValueError(
                f"Execution "
                f"'{execution_id}' "
                "was not found."
            )

        return execution

    def list_executions(
        self,
    ) -> list[Execution]:
        return self.store.list_all()

    def list_by_status(
        self,
        status: ExecutionStatus,
    ) -> list[Execution]:
        return self.store.list_by_status(
            status
        )

    def start_execution(
        self,
        execution: Execution,
        plan: Plan,
    ) -> Execution:
        self._validate_execution_plan_match(
            execution,
            plan,
        )

        if (
            execution.status
            != ExecutionStatus.PENDING
        ):
            raise ValueError(
                "Only pending executions "
                "can be started."
            )

        if (
            plan.status
            == PlanStatus.PENDING
        ):
            self.planner.start_plan(
                plan
            )

        elif (
            plan.status
            != PlanStatus.IN_PROGRESS
        ):
            raise ValueError(
                "Plan must be pending or "
                "in progress before execution "
                "can start."
            )

        execution.start()

        self._sync_step_execution_statuses(
            execution=execution,
            plan=plan,
        )

        self.store.save(
            execution
        )

        logger.info(
            "Started execution | "
            "execution_id=%s | "
            "plan_id=%s",
            execution.id,
            plan.id,
        )

        return execution

    def get_next_step(
        self,
        execution: Execution,
        plan: Plan,
    ) -> tuple[
        PlanStep,
        StepExecution,
    ] | None:
        self._validate_execution_plan_match(
            execution,
            plan,
        )

        if (
            execution.status
            != ExecutionStatus.RUNNING
        ):
            raise ValueError(
                "Execution must be running "
                "before selecting a step."
            )

        self.planner.refresh_step_readiness(
            plan
        )

        self._sync_step_execution_statuses(
            execution=execution,
            plan=plan,
        )

        plan_step = (
            self.planner.get_next_step(
                plan
            )
        )

        if plan_step is None:
            return None

        step_execution = (
            execution.get_step_execution(
                plan_step.id
            )
        )

        if step_execution is None:
            raise ValueError(
                f"Execution does not contain "
                f"plan step '{plan_step.id}'."
            )

        return (
            plan_step,
            step_execution,
        )

    def start_next_step(
        self,
        execution: Execution,
        plan: Plan,
    ) -> StepExecution | None:
        next_step = self.get_next_step(
            execution=execution,
            plan=plan,
        )

        if next_step is None:
            return None

        plan_step, step_execution = (
            next_step
        )

        self.planner.start_step(
            plan=plan,
            step_id=plan_step.id,
        )

        step_execution.start()

        execution.set_current_step(
            plan_step.id
        )

        self.store.save(
            execution
        )

        logger.info(
            "Started execution step | "
            "execution_id=%s | "
            "plan_step_id=%s | "
            "title=%s",
            execution.id,
            plan_step.id,
            plan_step.title,
        )

        return step_execution

    def complete_current_step(
        self,
        execution: Execution,
        plan: Plan,
        output=None,
        tool_execution_id: str | None = None,
    ) -> StepExecution:
        self._validate_execution_plan_match(
            execution,
            plan,
        )

        plan_step, step_execution = (
            self._get_current_step_pair(
                execution,
                plan,
            )
        )

        if (
            step_execution.status
            != StepExecutionStatus.RUNNING
        ):
            raise ValueError(
                "Current step execution "
                "is not running."
            )

        self.planner.complete_step(
            plan=plan,
            step_id=plan_step.id,
        )

        step_execution.complete(
            output=output,
            tool_execution_id=(
                tool_execution_id
            ),
        )

        execution.set_current_step(
            None
        )

        self._sync_step_execution_statuses(
            execution=execution,
            plan=plan,
        )

        self.store.save(
            execution
        )

        logger.info(
            "Completed execution step | "
            "execution_id=%s | "
            "plan_step_id=%s",
            execution.id,
            plan_step.id,
        )

        return step_execution

    def fail_current_step(
        self,
        execution: Execution,
        plan: Plan,
        error: str,
        error_code: str | None = None,
        tool_execution_id: str | None = None,
    ) -> StepExecution:
        self._validate_execution_plan_match(
            execution,
            plan,
        )

        plan_step, step_execution = (
            self._get_current_step_pair(
                execution,
                plan,
            )
        )

        if (
            step_execution.status
            != StepExecutionStatus.RUNNING
        ):
            raise ValueError(
                "Current step execution "
                "is not running."
            )

        self.planner.fail_step(
            plan=plan,
            step_id=plan_step.id,
        )

        step_execution.fail(
            error=error,
            error_code=error_code,
            tool_execution_id=(
                tool_execution_id
            ),
        )

        execution.set_current_step(
            None
        )

        self.store.save(
            execution
        )

        logger.warning(
            "Execution step failed | "
            "execution_id=%s | "
            "plan_step_id=%s | "
            "error=%s",
            execution.id,
            plan_step.id,
            error,
        )

        return step_execution

    def skip_current_step(
        self,
        execution: Execution,
        plan: Plan,
    ) -> StepExecution:
        self._validate_execution_plan_match(
            execution,
            plan,
        )

        plan_step, step_execution = (
            self._get_current_step_pair(
                execution,
                plan,
            )
        )

        if (
            step_execution.status
            != StepExecutionStatus.RUNNING
        ):
            raise ValueError(
                "Current step execution "
                "is not running."
            )

        self.planner.skip_step(
            plan=plan,
            step_id=plan_step.id,
        )

        step_execution.skip()

        execution.set_current_step(
            None
        )

        self.planner.refresh_step_readiness(
            plan
        )

        self._sync_step_execution_statuses(
            execution=execution,
            plan=plan,
        )

        self.store.save(
            execution
        )

        logger.info(
            "Skipped execution step | "
            "execution_id=%s | "
            "plan_step_id=%s",
            execution.id,
            plan_step.id,
        )

        return step_execution

    def pause_execution(
        self,
        execution: Execution,
    ) -> Execution:
        if (
            execution.status
            != ExecutionStatus.RUNNING
        ):
            raise ValueError(
                "Only running executions "
                "can be paused."
            )

        if execution.current_step_id:
            raise ValueError(
                "Cannot pause execution "
                "while a step is running."
            )

        execution.pause()

        self.store.save(
            execution
        )

        logger.info(
            "Paused execution | "
            "execution_id=%s",
            execution.id,
        )

        return execution

    def resume_execution(
        self,
        execution: Execution,
    ) -> Execution:
        if (
            execution.status
            != ExecutionStatus.PAUSED
        ):
            raise ValueError(
                "Only paused executions "
                "can be resumed."
            )

        execution.status = (
            ExecutionStatus.RUNNING
        )

        self.store.save(
            execution
        )

        logger.info(
            "Resumed execution | "
            "execution_id=%s",
            execution.id,
        )

        return execution

    def complete_execution(
        self,
        execution: Execution,
        plan: Plan,
    ) -> Execution:
        self._validate_execution_plan_match(
            execution,
            plan,
        )

        if (
            execution.status
            != ExecutionStatus.RUNNING
        ):
            raise ValueError(
                "Only running executions "
                "can be completed."
            )

        if execution.current_step_id:
            raise ValueError(
                "Cannot complete execution "
                "while a step is running."
            )

        unfinished_steps = [
            step_execution
            for step_execution
            in execution.step_executions
            if step_execution.status
            not in {
                StepExecutionStatus.COMPLETED,
                StepExecutionStatus.SKIPPED,
            }
        ]

        if unfinished_steps:
            raise ValueError(
                "Cannot complete execution "
                "while unfinished steps remain."
            )

        self._sync_plan_from_execution(
            execution=execution,
            plan=plan,
        )

        if (
            plan.status
            != PlanStatus.COMPLETED
        ):
            self.planner.complete_plan(
                plan
            )

        execution.complete()

        self.store.save(
            execution
        )

        logger.info(
            "Completed execution | "
            "execution_id=%s | "
            "plan_id=%s",
            execution.id,
            plan.id,
        )

        return execution

    def fail_execution(
        self,
        execution: Execution,
        plan: Plan,
        error: str,
        error_code: str | None = None,
    ) -> Execution:
        self._validate_execution_plan_match(
            execution,
            plan,
        )

        if execution.status in {
            ExecutionStatus.COMPLETED,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.FAILED,
        }:
            raise ValueError(
                "Execution is already in a "
                "terminal state."
            )

        execution.fail(
            error=error,
            error_code=error_code,
        )

        if (
            plan.status
            != PlanStatus.FAILED
        ):
            self.planner.fail_plan(
                plan
            )

        self.store.save(
            execution
        )

        logger.warning(
            "Execution failed | "
            "execution_id=%s | error=%s",
            execution.id,
            error,
        )

        return execution

    def cancel_execution(
        self,
        execution: Execution,
        plan: Plan,
    ) -> Execution:
        self._validate_execution_plan_match(
            execution,
            plan,
        )

        if execution.status in {
            ExecutionStatus.COMPLETED,
            ExecutionStatus.CANCELLED,
            ExecutionStatus.FAILED,
        }:
            raise ValueError(
                "Execution is already in a "
                "terminal state."
            )

        execution.cancel()

        if (
            plan.status
            != PlanStatus.CANCELLED
        ):
            self.planner.cancel_plan(
                plan
            )

        self.store.save(
            execution
        )

        logger.info(
            "Cancelled execution | "
            "execution_id=%s",
            execution.id,
        )

        return execution

    def delete_execution(
        self,
        execution_id: str,
    ) -> bool:
        deleted = self.store.delete(
            execution_id
        )

        if deleted:
            logger.info(
                "Deleted execution | "
                "execution_id=%s",
                execution_id,
            )

        return deleted

    def clear_executions(
        self,
    ) -> int:
        removed = self.store.clear()

        logger.info(
            "Cleared executions | "
            "removed=%s",
            removed,
        )

        return removed

    def _get_current_step_pair(
        self,
        execution: Execution,
        plan: Plan,
    ) -> tuple[
        PlanStep,
        StepExecution,
    ]:
        current_step_id = (
            execution.current_step_id
        )

        if current_step_id is None:
            raise ValueError(
                "Execution has no "
                "current step."
            )

        plan_step = self.planner.get_step(
            plan,
            current_step_id,
        )

        if plan_step is None:
            raise ValueError(
                f"Plan step "
                f"'{current_step_id}' "
                "was not found."
            )

        step_execution = (
            execution.get_step_execution(
                current_step_id
            )
        )

        if step_execution is None:
            raise ValueError(
                f"Execution does not contain "
                f"plan step "
                f"'{current_step_id}'."
            )

        return (
            plan_step,
            step_execution,
        )

    def _validate_execution_plan_match(
        self,
        execution: Execution,
        plan: Plan,
    ) -> None:
        if (
            execution.plan_id
            != plan.id
        ):
            raise ValueError(
                "Execution does not belong "
                "to the provided plan."
            )

    def _sync_step_execution_statuses(
        self,
        execution: Execution,
        plan: Plan,
    ) -> None:
        for plan_step in plan.steps:
            step_execution = (
                execution.get_step_execution(
                    plan_step.id
                )
            )

            if step_execution is None:
                continue

            step_execution.status = (
                self._map_step_status(
                    plan_step.status
                )
            )

    def _sync_plan_from_execution(
        self,
        execution: Execution,
        plan: Plan,
    ) -> None:
        for step_execution in (
            execution.step_executions
        ):
            plan_step = (
                self.planner.get_step(
                    plan,
                    step_execution.plan_step_id,
                )
            )

            if plan_step is None:
                raise ValueError(
                    f"Plan step "
                    f"'{step_execution.plan_step_id}' "
                    "was not found."
                )

            if (
                step_execution.status
                == StepExecutionStatus.COMPLETED
            ):
                plan_step.status = (
                    PlanStepStatus.COMPLETED
                )

            elif (
                step_execution.status
                == StepExecutionStatus.SKIPPED
            ):
                plan_step.status = (
                    PlanStepStatus.SKIPPED
                )

            elif (
                step_execution.status
                == StepExecutionStatus.FAILED
            ):
                plan_step.status = (
                    PlanStepStatus.FAILED
                )

            elif (
                step_execution.status
                == StepExecutionStatus.RUNNING
            ):
                plan_step.status = (
                    PlanStepStatus.IN_PROGRESS
                )

            elif (
                step_execution.status
                == StepExecutionStatus.READY
            ):
                plan_step.status = (
                    PlanStepStatus.READY
                )

            else:
                plan_step.status = (
                    PlanStepStatus.PENDING
                )

    def _map_step_status(
        self,
        status: PlanStepStatus,
    ) -> StepExecutionStatus:
        mapping = {
            PlanStepStatus.PENDING:
                StepExecutionStatus.PENDING,

            PlanStepStatus.READY:
                StepExecutionStatus.READY,

            PlanStepStatus.IN_PROGRESS:
                StepExecutionStatus.RUNNING,

            PlanStepStatus.COMPLETED:
                StepExecutionStatus.COMPLETED,

            PlanStepStatus.FAILED:
                StepExecutionStatus.FAILED,

            PlanStepStatus.SKIPPED:
                StepExecutionStatus.SKIPPED,
        }

        return mapping[status]
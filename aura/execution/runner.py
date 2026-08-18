from aura.core.logger import logger
from aura.execution.binding import ToolBindingManager
from aura.execution.guards import ExecutionGuard
from aura.execution.manager import ExecutionManager
from aura.execution.models import (
    Execution,
    ExecutionStatus,
    StepExecution,
    StepExecutionStatus,
)
from aura.execution.retry import RetryPolicy
from aura.planning.models import (
    Plan,
    PlanStatus,
)
from aura.safety.authorizer import ExecutionAuthorizer
from aura.safety.models import (
    PermissionDecision,
    SafetyContext,
)
from aura.safety.reliability import (
    ReliabilityManager,
)
from aura.tools.executor import ToolExecutor
from aura.tools.models import ToolResult


class ExecutionRunner:
    def __init__(
        self,
        execution_manager: ExecutionManager,
        tool_executor: ToolExecutor,
        tool_binding_manager: ToolBindingManager | None = None,
        retry_policy: RetryPolicy | None = None,
        execution_guard: ExecutionGuard | None = None,
        execution_authorizer: ExecutionAuthorizer | None = None,
        reliability_manager: ReliabilityManager | None = None,
    ):
        self.execution_manager = (
            execution_manager
        )

        self.tool_executor = (
            tool_executor
        )

        self.tool_binding_manager = (
            tool_binding_manager
        )

        self.retry_policy = (
            retry_policy
            or RetryPolicy()
        )

        self.execution_guard = (
            execution_guard
            or ExecutionGuard()
        )

        self.execution_authorizer = (
            execution_authorizer
        )

        self.reliability_manager = (
            reliability_manager
        )

    async def execute_current_step(
        self,
        execution: Execution,
        plan: Plan,
    ) -> ToolResult:
        if (
            execution.status
            != ExecutionStatus.RUNNING
        ):
            raise ValueError(
                "Execution must be running."
            )

        if execution.current_step_id is None:
            raise ValueError(
                "Execution has no current step."
            )

        step_execution = (
            execution.get_step_execution(
                execution.current_step_id
            )
        )

        if step_execution is None:
            raise ValueError(
                "Current step execution "
                "was not found."
            )

        if (
            step_execution.status
            != StepExecutionStatus.RUNNING
        ):
            raise ValueError(
                "Current step execution "
                "is not running."
            )

        if not step_execution.tool_name:
            raise ValueError(
                "Current step has no "
                "bound tool."
            )

        if (
            self.execution_authorizer
            is not None
        ):
            self._authorize_step(
                execution=execution,
                plan=plan,
                step_execution=step_execution,
            )

        self._check_reliability(
            step_execution
        )

        result = await self._execute_with_retry(
            execution=execution,
            step_execution=step_execution,
        )

        self._record_reliability_result(
            step_execution=step_execution,
            result=result,
        )

        if result.success:
            (
                self.execution_manager
                .complete_current_step(
                    execution=execution,
                    plan=plan,
                    output=result.output,
                    tool_execution_id=(
                        result.execution_id
                    ),
                )
            )

            logger.info(
                "Bound tool execution "
                "completed successfully | "
                "execution_id=%s | "
                "tool=%s",
                execution.id,
                step_execution.tool_name,
            )

        else:
            (
                self.execution_manager
                .fail_current_step(
                    execution=execution,
                    plan=plan,
                    error=(
                        result.error
                        or "Tool execution failed."
                    ),
                    error_code=(
                        result.error_code
                    ),
                    tool_execution_id=(
                        result.execution_id
                    ),
                )
            )

            logger.warning(
                "Bound tool execution failed | "
                "execution_id=%s | "
                "tool=%s | "
                "error=%s",
                execution.id,
                step_execution.tool_name,
                result.error,
            )

        return result

    def _authorize_step(
        self,
        execution: Execution,
        plan: Plan,
        step_execution: StepExecution,
    ) -> None:
        if self.execution_authorizer is None:
            return

        metadata = {
            "step_title":
                step_execution.title,
        }

        existing_approval_id = (
            step_execution.metadata.get(
                "approval_id"
            )
        )

        if existing_approval_id:
            metadata[
                "approval_id"
            ] = existing_approval_id

        context = SafetyContext(
            tool_name=(
                step_execution.tool_name
            ),
            action="execute",
            execution_id=execution.id,
            plan_id=plan.id,
            step_id=(
                step_execution.plan_step_id
            ),
            arguments=dict(
                step_execution.arguments
            ),
            metadata=metadata,
        )

        decision = (
            self.execution_authorizer
            .authorize(
                context
            )
        )

        step_execution.metadata[
            "safety_decision_id"
        ] = decision.id

        step_execution.metadata[
            "risk_level"
        ] = decision.risk_level.value

        step_execution.metadata[
            "permission_decision"
        ] = decision.decision.value

        step_execution.metadata[
            "approval_status"
        ] = decision.approval_status.value

        approval_id = (
            decision.context.metadata.get(
                "approval_id"
            )
        )

        if approval_id:
            step_execution.metadata[
                "approval_id"
            ] = approval_id

        if (
            decision.decision
            == PermissionDecision.ALLOW
        ):
            return

        if (
            decision.decision
            == PermissionDecision
            .REQUIRE_APPROVAL
        ):
            raise PermissionError(
                "Tool execution requires "
                "approval."
            )

        raise PermissionError(
            "Tool execution was denied "
            "by safety policy."
        )

    def _check_reliability(
        self,
        step_execution: StepExecution,
    ) -> None:
        if (
            self.reliability_manager
            is None
        ):
            return

        tool_name = (
            step_execution.tool_name
        )

        if tool_name is None:
            return

        if not (
            self.reliability_manager
            .can_execute(
                tool_name
            )
        ):
            state = (
                self.reliability_manager
                .get_state(
                    tool_name
                )
            )

            step_execution.metadata[
                "circuit_open"
            ] = True

            step_execution.metadata[
                "reliability_failure_count"
            ] = state.failure_count

            raise RuntimeError(
                f"Tool '{tool_name}' "
                "is temporarily unavailable "
                "because its reliability "
                "circuit is open."
            )

    def _record_reliability_result(
        self,
        step_execution: StepExecution,
        result: ToolResult,
    ) -> None:
        if (
            self.reliability_manager
            is None
        ):
            return

        tool_name = (
            step_execution.tool_name
        )

        if tool_name is None:
            return

        if result.success:
            state = (
                self.reliability_manager
                .record_success(
                    tool_name
                )
            )

        else:
            state = (
                self.reliability_manager
                .record_failure(
                    tool_name=tool_name,
                    error=result.error,
                )
            )

        step_execution.metadata[
            "reliability_failure_count"
        ] = state.failure_count

        step_execution.metadata[
            "reliability_success_count"
        ] = state.success_count

        step_execution.metadata[
            "circuit_open"
        ] = state.circuit_open

    async def _execute_with_retry(
        self,
        execution: Execution,
        step_execution: StepExecution,
    ) -> ToolResult:
        attempt = 0

        while True:
            attempt += 1

            logger.info(
                "Executing tool attempt | "
                "execution_id=%s | "
                "plan_step_id=%s | "
                "tool=%s | "
                "attempt=%s",
                execution.id,
                step_execution.plan_step_id,
                step_execution.tool_name,
                attempt,
            )

            result = (
                await self.tool_executor
                .execute(
                    tool_name=(
                        step_execution.tool_name
                    ),
                    arguments=(
                        step_execution.arguments
                    ),
                )
            )

            step_execution.metadata[
                "attempt_count"
            ] = attempt

            if result.success:
                return result

            should_retry = (
                self.retry_policy
                .should_retry(
                    attempt=attempt,
                    error_code=(
                        result.error_code
                    ),
                )
            )

            if not should_retry:
                return result

            logger.warning(
                "Retrying tool execution | "
                "execution_id=%s | "
                "tool=%s | "
                "attempt=%s | "
                "error_code=%s",
                execution.id,
                step_execution.tool_name,
                attempt,
                result.error_code,
            )

    def ensure_tool_binding(
        self,
        execution: Execution,
        plan: Plan,
        step_execution: StepExecution,
    ) -> StepExecution:
        if step_execution.tool_name:
            return step_execution

        if (
            self.tool_binding_manager
            is None
        ):
            raise ValueError(
                f"Step "
                f"'{step_execution.title}' "
                "has no bound tool."
            )

        plan_step = (
            self.execution_manager
            .planner
            .get_step(
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

        arguments = self._infer_arguments(
            plan_step=plan_step,
            execution=execution,
        )

        logger.info(
            "Automatically binding tool | "
            "execution_id=%s | "
            "plan_step_id=%s | "
            "title=%s",
            execution.id,
            plan_step.id,
            plan_step.title,
        )

        return (
            self.tool_binding_manager
            .auto_bind(
                plan_step=plan_step,
                step_execution=step_execution,
                arguments=arguments,
            )
        )

    async def start_and_execute_next_step(
        self,
        execution: Execution,
        plan: Plan,
    ) -> ToolResult | None:
        next_step = (
            self.execution_manager
            .get_next_step(
                execution=execution,
                plan=plan,
            )
        )

        if next_step is None:
            return None

        _, step_execution = next_step

        self.ensure_tool_binding(
            execution=execution,
            plan=plan,
            step_execution=step_execution,
        )

        started_step = (
            self.execution_manager
            .start_next_step(
                execution=execution,
                plan=plan,
            )
        )

        if started_step is None:
            return None

        return await self.execute_current_step(
            execution=execution,
            plan=plan,
        )

    async def run_execution(
        self,
        execution: Execution,
        plan: Plan,
        stop_on_failure: bool = True,
    ) -> Execution:
        try:
            (
                self.execution_guard
                .validate_before_run(
                    execution
                )
            )

        except ValueError as exc:
            self._fail_guarded_execution(
                execution=execution,
                plan=plan,
                error=str(exc),
            )

            return execution

        if (
            execution.status
            == ExecutionStatus.PENDING
        ):
            (
                self.execution_manager
                .start_execution(
                    execution=execution,
                    plan=plan,
                )
            )

        elif (
            execution.status
            != ExecutionStatus.RUNNING
        ):
            raise ValueError(
                "Execution must be pending "
                "or running."
            )

        iteration = 0

        while (
            execution.status
            == ExecutionStatus.RUNNING
        ):
            iteration += 1

            execution.metadata[
                "iteration_count"
            ] = iteration

            try:
                (
                    self.execution_guard
                    .validate_iteration(
                        execution=execution,
                        iteration=iteration,
                    )
                )

            except ValueError as exc:
                self._fail_guarded_execution(
                    execution=execution,
                    plan=plan,
                    error=str(exc),
                )

                return execution

            try:
                result = (
                    await self
                    .start_and_execute_next_step(
                        execution=execution,
                        plan=plan,
                    )
                )

            except PermissionError as exc:
                self._pause_for_approval(
                    execution=execution,
                    plan=plan,
                    error=str(exc),
                )

                return execution

            except RuntimeError as exc:
                (
                    self.execution_manager
                    .fail_execution(
                        execution=execution,
                        plan=plan,
                        error=str(exc),
                        error_code=(
                            "reliability_circuit_open"
                        ),
                    )
                )

                logger.warning(
                    "Execution stopped by "
                    "reliability protection | "
                    "execution_id=%s | "
                    "error=%s",
                    execution.id,
                    exc,
                )

                return execution

            except ValueError as exc:
                (
                    self.execution_manager
                    .fail_execution(
                        execution=execution,
                        plan=plan,
                        error=str(exc),
                        error_code=(
                            "automatic_binding_failed"
                        ),
                    )
                )

                return execution

            if result is None:
                break

            if (
                not result.success
                and stop_on_failure
            ):
                (
                    self.execution_manager
                    .fail_execution(
                        execution=execution,
                        plan=plan,
                        error=(
                            result.error
                            or "Execution step failed."
                        ),
                        error_code=(
                            result.error_code
                        ),
                    )
                )

                return execution

        if (
            execution.status
            == ExecutionStatus.RUNNING
        ):
            unfinished_steps = [
                step
                for step
                in execution.step_executions
                if step.status
                not in {
                    StepExecutionStatus.COMPLETED,
                    StepExecutionStatus.SKIPPED,
                }
            ]

            if not unfinished_steps:
                (
                    self.execution_manager
                    .complete_execution(
                        execution=execution,
                        plan=plan,
                    )
                )

        return execution

    def resume_after_approval(
        self,
        execution: Execution,
        plan: Plan,
    ) -> None:
        if (
            execution.status
            != ExecutionStatus.PAUSED
        ):
            raise ValueError(
                "Only paused executions "
                "can resume after approval."
            )

        current_step_id = (
            execution.current_step_id
        )

        if current_step_id is None:
            raise ValueError(
                "Execution has no "
                "pending approval step."
            )

        step_execution = (
            execution.get_step_execution(
                current_step_id
            )
        )

        if step_execution is None:
            raise ValueError(
                "Pending approval step "
                "was not found."
            )

        approval_id = (
            step_execution.metadata.get(
                "approval_id"
            )
        )

        if not approval_id:
            raise ValueError(
                "Current step has no "
                "approval request."
            )

        if (
            self.execution_authorizer
            is None
        ):
            raise ValueError(
                "Execution authorizer "
                "is not configured."
            )

        approval = (
            self.execution_authorizer
            .approval_manager
            .get(
                approval_id
            )
        )

        if approval is None:
            raise ValueError(
                "Approval request "
                "was not found."
            )

        if (
            approval.status.value
            != "approved"
        ):
            raise ValueError(
                "Approval request has "
                "not been approved."
            )

        execution.status = (
            ExecutionStatus.RUNNING
        )

        execution.error = None
        execution.error_code = None

        if (
            plan.status
            == PlanStatus.FAILED
        ):
            plan.status = (
                PlanStatus.IN_PROGRESS
            )

        self.execution_manager.store.save(
            execution
        )

        logger.info(
            "Execution resumed after "
            "approval | "
            "execution_id=%s | "
            "approval_id=%s",
            execution.id,
            approval_id,
        )

    def _pause_for_approval(
        self,
        execution: Execution,
        plan: Plan,
        error: str,
    ) -> None:
        execution.status = (
            ExecutionStatus.PAUSED
        )

        execution.error = error

        execution.error_code = (
            "approval_required"
        )

        self.execution_manager.store.save(
            execution
        )

        logger.warning(
            "Execution paused for approval | "
            "execution_id=%s | "
            "error=%s",
            execution.id,
            error,
        )

    def _fail_guarded_execution(
        self,
        execution: Execution,
        plan: Plan,
        error: str,
    ) -> None:
        if (
            execution.status
            == ExecutionStatus.PENDING
        ):
            execution.start()

        (
            self.execution_manager
            .fail_execution(
                execution=execution,
                plan=plan,
                error=error,
                error_code=(
                    "execution_limit_exceeded"
                ),
            )
        )

    def _infer_arguments(
        self,
        plan_step,
        execution: Execution,
    ) -> dict:
        metadata = (
            plan_step.metadata
            or {}
        )

        explicit_arguments = (
            metadata.get(
                "tool_arguments"
            )
        )

        if isinstance(
            explicit_arguments,
            dict,
        ):
            return dict(
                explicit_arguments
            )

        title = (
            plan_step.title
            .strip()
            .lower()
        )

        if (
            "current time" in title
            or "current date" in title
            or "system" in title
            or "environment" in title
        ):
            return {}

        if (
            "text" in title
            or "word" in title
            or "character" in title
        ):
            text = metadata.get(
                "text"
            )

            if isinstance(
                text,
                str,
            ):
                return {
                    "text": text,
                }

        return {}
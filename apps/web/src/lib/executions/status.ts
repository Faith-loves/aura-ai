import type { ExecutionResponse, ExecutionStatus, StepExecutionResponse, StepExecutionStatus } from "@/types/api";

export const EXECUTION_TERMINAL_STATUSES: ExecutionStatus[] = ["completed", "failed", "cancelled"];
export const STEP_FINISHED_STATUSES: StepExecutionStatus[] = ["completed", "skipped"];

export function isExecutionTerminal(status: ExecutionStatus) {
  return EXECUTION_TERMINAL_STATUSES.includes(status);
}

export function isExecutionActive(status: ExecutionStatus) {
  return status === "pending" || status === "running" || status === "paused";
}

export function isStepFinished(status: StepExecutionStatus) {
  return STEP_FINISHED_STATUSES.includes(status);
}

export function getExecutionProgress(execution: ExecutionResponse) {
  const total = execution.step_executions.length;
  const completed = execution.step_executions.filter((step) => isStepFinished(step.status)).length;
  const failed = execution.step_executions.filter((step) => step.status === "failed").length;
  const percent = total > 0 ? Math.round((completed / total) * 100) : 0;

  return { total, completed, failed, percent };
}

export function getCurrentStep(execution: ExecutionResponse): StepExecutionResponse | null {
  if (execution.current_step_id) {
    return execution.step_executions.find((step) => step.plan_step_id === execution.current_step_id || step.id === execution.current_step_id) ?? null;
  }

  return execution.step_executions.find((step) => step.status === "running") ?? null;
}

export function getNextVisibleStep(execution: ExecutionResponse): StepExecutionResponse | null {
  return getCurrentStep(execution) ?? execution.step_executions.find((step) => step.status === "ready") ?? execution.step_executions.find((step) => step.status === "pending") ?? null;
}

export function titleCaseStatus(status: string) {
  return status.split("_").map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`).join(" ");
}

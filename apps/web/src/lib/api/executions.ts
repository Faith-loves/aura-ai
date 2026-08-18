import type {
  CreateExecutionRequest,
  ExecutionResponse,
} from "@/types/api";

import {
  apiFetch,
} from "./client";

export function getExecutions() {
  return apiFetch<ExecutionResponse[]>("/executions");
}

export function getExecution(executionId: string) {
  return apiFetch<ExecutionResponse>(`/executions/${encodeURIComponent(executionId)}`);
}

export function createExecution(request: CreateExecutionRequest) {
  return apiFetch<ExecutionResponse>("/executions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      metadata: {},
      ...request,
    }),
  });
}

export function startExecution(executionId: string) {
  return apiFetch<ExecutionResponse>(`/executions/${encodeURIComponent(executionId)}/start`, {
    method: "POST",
  });
}

export function runExecution(executionId: string) {
  return apiFetch<ExecutionResponse>(`/executions/${encodeURIComponent(executionId)}/run`, {
    method: "POST",
  });
}

export function pauseExecution(executionId: string) {
  return apiFetch<ExecutionResponse>(`/executions/${encodeURIComponent(executionId)}/pause`, {
    method: "POST",
  });
}

export function resumeExecution(executionId: string) {
  return apiFetch<ExecutionResponse>(`/executions/${encodeURIComponent(executionId)}/resume`, {
    method: "POST",
  });
}

export function cancelExecution(executionId: string) {
  return apiFetch<ExecutionResponse>(`/executions/${encodeURIComponent(executionId)}/cancel`, {
    method: "POST",
  });
}

export function deleteExecution(executionId: string) {
  return apiFetch<{ success: boolean; execution_id: string }>(`/executions/${encodeURIComponent(executionId)}`, {
    method: "DELETE",
  });
}

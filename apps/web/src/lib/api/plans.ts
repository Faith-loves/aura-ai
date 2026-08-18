import type {
  CreatePlanRequest,
  PlanResponse,
  UpdateStepPriorityRequest,
} from "@/types/api";

import {
  apiFetch,
} from "./client";

export function getPlans() {
  return apiFetch<PlanResponse[]>("/plans");
}

export function getPlan(planId: string) {
  return apiFetch<PlanResponse>(`/plans/${encodeURIComponent(planId)}`);
}

export function createPlan(request: CreatePlanRequest) {
  return apiFetch<PlanResponse>("/plans", {
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

export function startPlan(planId: string) {
  return apiFetch<PlanResponse>(`/plans/${encodeURIComponent(planId)}/start`, {
    method: "POST",
  });
}

export function startPlanStep(planId: string, stepId: string) {
  return apiFetch<PlanResponse>(`/plans/${encodeURIComponent(planId)}/steps/${encodeURIComponent(stepId)}/start`, {
    method: "POST",
  });
}

export function completePlanStep(planId: string, stepId: string) {
  return apiFetch<PlanResponse>(`/plans/${encodeURIComponent(planId)}/steps/${encodeURIComponent(stepId)}/complete`, {
    method: "POST",
  });
}

export function updateStepPriority(planId: string, stepId: string, priority: number) {
  const request: UpdateStepPriorityRequest = {
    priority,
  };

  return apiFetch<PlanResponse>(`/plans/${encodeURIComponent(planId)}/steps/${encodeURIComponent(stepId)}/priority`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });
}

export function completePlan(planId: string) {
  return apiFetch<PlanResponse>(`/plans/${encodeURIComponent(planId)}/complete`, {
    method: "POST",
  });
}

export function deletePlan(planId: string) {
  return apiFetch<{ success: boolean; plan_id: string }>(`/plans/${encodeURIComponent(planId)}`, {
    method: "DELETE",
  });
}

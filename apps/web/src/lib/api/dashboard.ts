import type {
  ApprovalResponse,
  AuditResponse,
  ExecutionResponse,
  HealthResponse,
  MemoryStatsResponse,
  ModelsResponse,
  ReliabilityStateResponse,
  RootResponse,
  SafetyPolicyResponse,
  ToolResponse,
} from "@/types/api";

import { apiFetch } from "./client";

export function getRoot() {
  return apiFetch<RootResponse>("/");
}

export function getHealth() {
  return apiFetch<HealthResponse>("/health");
}

export function getModels() {
  return apiFetch<ModelsResponse>("/models");
}

export function getTools() {
  return apiFetch<ToolResponse[]>("/tools");
}

export function getExecutions() {
  return apiFetch<ExecutionResponse[]>("/executions");
}

export function getMemoryStats() {
  return apiFetch<MemoryStatsResponse>("/memory/stats");
}

export function getSafetyPolicy() {
  return apiFetch<SafetyPolicyResponse>("/safety/policy");
}

export function getApprovals() {
  return apiFetch<ApprovalResponse[]>("/safety/approvals");
}

export function getAuditRecords() {
  return apiFetch<AuditResponse[]>("/safety/audit");
}

export function getReliabilityStates() {
  return apiFetch<ReliabilityStateResponse[]>("/safety/reliability");
}

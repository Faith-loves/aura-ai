import { apiFetch } from "@/lib/api/client";
import type {
  ApprovalDecisionRequest,
  ApprovalResponse,
  AuditResponse,
  ReliabilityStateResponse,
  SafetyPolicyResponse,
} from "@/types/api";

function jsonBody(payload: unknown) {
  return JSON.stringify(payload);
}

export function getSafetyPolicy() {
  return apiFetch<SafetyPolicyResponse>("/safety/policy");
}

export function getApprovals() {
  return apiFetch<ApprovalResponse[]>("/safety/approvals");
}

export function getApproval(approvalId: string) {
  return apiFetch<ApprovalResponse>(`/safety/approvals/${encodeURIComponent(approvalId)}`);
}

export function approveApproval(approvalId: string, request: ApprovalDecisionRequest) {
  return apiFetch<ApprovalResponse>(`/safety/approvals/${encodeURIComponent(approvalId)}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonBody(request),
  });
}

export function rejectApproval(approvalId: string, request: ApprovalDecisionRequest) {
  return apiFetch<ApprovalResponse>(`/safety/approvals/${encodeURIComponent(approvalId)}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonBody(request),
  });
}

export function getAuditLog() {
  return apiFetch<AuditResponse[]>("/safety/audit");
}

export function getReliabilityStates() {
  return apiFetch<ReliabilityStateResponse[]>("/safety/reliability");
}

export function resetReliabilityState(toolName: string) {
  return apiFetch<ReliabilityStateResponse>(`/safety/reliability/${encodeURIComponent(toolName)}/reset`, {
    method: "POST",
  });
}

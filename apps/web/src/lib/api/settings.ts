import { apiFetch, API_BASE_URL } from "@/lib/api/client";
import type { HealthResponse, ModelsResponse, ReliabilityStateResponse, RootResponse, SafetyPolicyResponse } from "@/types/api";

export function getRuntimeInfo() {
  return apiFetch<RootResponse>("/");
}

export function getSettingsHealth() {
  return apiFetch<HealthResponse>("/health");
}

export function getModelProviders() {
  return apiFetch<ModelsResponse>("/models");
}

export function getSettingsSafetyPolicy() {
  return apiFetch<SafetyPolicyResponse>("/safety/policy");
}

export function getSettingsReliabilityStates() {
  return apiFetch<ReliabilityStateResponse[]>("/safety/reliability");
}

export { API_BASE_URL };

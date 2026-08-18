import { apiFetch } from "@/lib/api/client";
import type { ExecuteToolRequest, ToolExecutionResponse, ToolResponse } from "@/types/api";

function jsonBody(payload: unknown) {
  return JSON.stringify(payload);
}

export function getTools() {
  return apiFetch<ToolResponse[]>("/tools");
}

export function searchTools(query: string) {
  return apiFetch<ToolResponse[]>(`/tools/search?query=${encodeURIComponent(query)}`);
}

export function executeTool(toolName: string, request: ExecuteToolRequest) {
  return apiFetch<ToolExecutionResponse>(`/tools/${encodeURIComponent(toolName)}/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonBody(request),
  });
}

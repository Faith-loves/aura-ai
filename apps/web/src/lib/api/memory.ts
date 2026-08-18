import { apiFetch } from "@/lib/api/client";
import type {
  CreateMemoryRequest,
  ImportMemoryRequest,
  MemoryActionResponse,
  MemoryExportResponse,
  MemoryResponse,
  MemorySearchResult,
  MemoryStatsResponse,
  RestoreMemoryRequest,
  SearchMemoryRequest,
} from "@/types/api";

function jsonBody(payload: unknown) {
  return JSON.stringify(payload);
}

function queryString(params: Record<string, string | number | boolean | undefined>) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) search.set(key, String(value));
  }
  const serialized = search.toString();
  return serialized ? `?${serialized}` : "";
}

export function getMemories() {
  return apiFetch<MemoryResponse[]>("/memory");
}

export function getMemory(memoryId: string) {
  return apiFetch<MemoryResponse>(`/memory/${encodeURIComponent(memoryId)}`);
}

export function getMemoryStats() {
  return apiFetch<MemoryStatsResponse>("/memory/stats");
}

export function searchMemories(request: SearchMemoryRequest) {
  return apiFetch<MemorySearchResult[]>("/memory/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonBody(request),
  });
}

export function createMemory(request: CreateMemoryRequest) {
  return apiFetch<MemoryResponse>("/memory", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonBody(request),
  });
}

export function deleteMemory(memoryId: string) {
  return apiFetch<MemoryActionResponse>(`/memory/${encodeURIComponent(memoryId)}`, {
    method: "DELETE",
  });
}

export function clearAllMemory() {
  return apiFetch<MemoryActionResponse>("/memory", {
    method: "DELETE",
  });
}

export function exportMemory() {
  return apiFetch<MemoryExportResponse>("/memory/export");
}

export function backupMemory() {
  return apiFetch<MemoryActionResponse>("/memory/backup", {
    method: "POST",
  });
}

export function importMemory(request: ImportMemoryRequest) {
  return apiFetch<MemoryActionResponse>("/memory/import", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonBody(request),
  });
}

export function restoreMemory(request: RestoreMemoryRequest) {
  return apiFetch<MemoryActionResponse>("/memory/restore", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: jsonBody(request),
  });
}

export function cleanupMemory(params: { min_importance?: number; max_access_count?: number; older_than_days?: number }) {
  return apiFetch<MemoryActionResponse>(`/memory/cleanup${queryString(params)}`, {
    method: "POST",
  });
}

export function cleanupContaminatedMemory() {
  return apiFetch<MemoryActionResponse>("/memory/cleanup-contaminated", {
    method: "POST",
  });
}

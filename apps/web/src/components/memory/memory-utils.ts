export const MEMORY_TYPES = ["conversation", "fact", "preference", "project", "task", "system"] as const;

export function label(value: string) {
  return value.split("_").map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`).join(" ");
}

export function shortId(value: string) {
  return value.length > 14 ? `${value.slice(0, 8)}...${value.slice(-4)}` : value;
}

export function formatNumber(value: number, digits = 2) {
  return Number.isInteger(value) ? String(value) : value.toFixed(digits);
}

export function hasMetadata(metadata: Record<string, unknown>) {
  return Object.keys(metadata).length > 0;
}

export function formatJson(value: unknown) {
  if (value === null || value === undefined) return "None";
  if (typeof value === "object" && Object.keys(value as Record<string, unknown>).length === 0) return "None";
  return JSON.stringify(value, null, 2);
}

import type { JsonValue, ToolParameterResponse, ToolResponse } from "@/types/api";

export function label(value: string) {
  return value.split("_").map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`).join(" ");
}

export function formatJson(value: unknown) {
  if (value === null || value === undefined) return "None";
  if (typeof value === "string") return value;
  return JSON.stringify(value, null, 2);
}

export function defaultParameterValue(parameter: ToolParameterResponse): string | boolean {
  if (parameter.default !== null) {
    if (typeof parameter.default === "boolean") return parameter.default;
    if (typeof parameter.default === "string" || typeof parameter.default === "number") return String(parameter.default);
    return JSON.stringify(parameter.default);
  }

  if (parameter.parameter_type === "boolean") return false;
  return "";
}

export function coerceParameterValue(parameter: ToolParameterResponse, value: string | boolean): JsonValue | undefined {
  if (parameter.parameter_type === "boolean") return Boolean(value);
  const text = typeof value === "string" ? value.trim() : String(value);
  if (!text && !parameter.required) return undefined;

  if (parameter.parameter_type === "integer") {
    const parsed = Number.parseInt(text, 10);
    if (Number.isNaN(parsed)) throw new Error(`${parameter.name} must be an integer.`);
    return parsed;
  }

  if (parameter.parameter_type === "float") {
    const parsed = Number.parseFloat(text);
    if (Number.isNaN(parsed)) throw new Error(`${parameter.name} must be a number.`);
    return parsed;
  }

  if (parameter.parameter_type === "list" || parameter.parameter_type === "object") {
    if (!text && !parameter.required) return undefined;
    const parsed = JSON.parse(text) as JsonValue;
    if (parameter.parameter_type === "list" && !Array.isArray(parsed)) throw new Error(`${parameter.name} must be a JSON array.`);
    if (parameter.parameter_type === "object" && (!parsed || typeof parsed !== "object" || Array.isArray(parsed))) throw new Error(`${parameter.name} must be a JSON object.`);
    return parsed;
  }

  return text;
}

export function toolSafetyLabel(tool: ToolResponse) {
  if (tool.dangerous) return "Dangerous";
  if (tool.requires_confirmation) return "Confirmation Required";
  return "Standard";
}

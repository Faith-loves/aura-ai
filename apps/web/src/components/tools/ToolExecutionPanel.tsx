"use client";

import Link from "next/link";
import { AlertTriangle, Play } from "lucide-react";
import { useMemo, useState } from "react";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { executeTool } from "@/lib/api/tools";
import type { JsonValue, ReliabilityStateResponse, ToolExecutionResponse, ToolParameterResponse, ToolResponse } from "@/types/api";

import { coerceParameterValue, defaultParameterValue, formatJson, label } from "./tool-utils";

type ToolExecutionPanelProps = {
  tool: ToolResponse;
  reliabilityState: ReliabilityStateResponse | null;
};

type FieldValue = string | boolean;

function formatDate(value: string | null) {
  if (!value) return "Not available";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Unavailable" : date.toLocaleString();
}

function formatDuration(value: number | null) {
  if (value === null) return "Not available";
  return `${Math.round(value)}ms`;
}

export default function ToolExecutionPanel({ tool, reliabilityState }: ToolExecutionPanelProps) {
  const [values, setValues] = useState<Record<string, FieldValue>>(() => Object.fromEntries(tool.parameters.map((parameter) => [parameter.name, defaultParameterValue(parameter)])));
  const [advancedArguments, setAdvancedArguments] = useState("");
  const [useAdvanced, setUseAdvanced] = useState(false);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<ToolExecutionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const circuitOpen = Boolean(reliabilityState?.circuit_open);
  const needsConfirmation = tool.dangerous || tool.requires_confirmation;

  const simpleParameters = useMemo(() => tool.parameters.every((parameter) => ["string", "integer", "float", "boolean"].includes(parameter.parameter_type)), [tool.parameters]);

  function buildArguments() {
    if (useAdvanced || !simpleParameters) {
      if (!advancedArguments.trim()) return {};
      const parsed = JSON.parse(advancedArguments) as unknown;
      if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("Advanced arguments must be a JSON object.");
      return parsed as Record<string, JsonValue>;
    }

    const args: Record<string, JsonValue> = {};
    for (const parameter of tool.parameters) {
      const coerced = coerceParameterValue(parameter, values[parameter.name] ?? "");
      if (coerced !== undefined) args[parameter.name] = coerced;
    }
    return args;
  }

  async function handleRun() {
    setError(null);
    setResult(null);

    let args: Record<string, JsonValue>;
    try {
      args = buildArguments();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Invalid arguments.");
      return;
    }

    if (needsConfirmation && !window.confirm(`Confirm tool execution for ${tool.name}? AURA identifies this tool as requiring additional care. This frontend confirmation does not replace backend safety enforcement.`)) return;

    setRunning(true);
    try {
      setResult(await executeTool(tool.name, { arguments: args }));
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Tool execution failed.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <Card className="p-5 sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">Run Tool</h2>
          <p className="mt-1 text-sm text-[#94A3B8]">Manual execution uses the backend tool executor. Backend safety remains authoritative.</p>
        </div>
        {needsConfirmation && <Badge variant="warning">Confirmation Required</Badge>}
      </div>

      {circuitOpen && (
        <div className="mt-5 rounded-2xl border border-[#EF4444]/30 bg-[#EF4444]/10 p-4 text-sm text-[#FCA5A5]">
          <div className="flex gap-2"><AlertTriangle size={18} /><p>AURA&apos;s reliability protection has paused this tool after repeated failures. Manual execution is disabled while the circuit is open.</p></div>
        </div>
      )}

      {!simpleParameters && <p className="mt-5 rounded-xl border border-[#F59E0B]/30 bg-[#F59E0B]/10 px-3 py-2 text-sm text-[#FCD34D]">This tool uses complex parameters, so advanced JSON arguments are enabled.</p>}

      <div className="mt-5 space-y-4">
        {simpleParameters && !useAdvanced && tool.parameters.map((parameter) => <ParameterInput key={parameter.name} parameter={parameter} value={values[parameter.name] ?? ""} onChange={(value) => setValues((current) => ({ ...current, [parameter.name]: value }))} disabled={running || circuitOpen} />)}
        {(useAdvanced || !simpleParameters) && <label className="block text-sm font-medium text-[#CBD5E1]">Advanced JSON arguments<textarea value={advancedArguments} onChange={(event) => setAdvancedArguments(event.target.value)} className="mt-2 min-h-36 w-full resize-y rounded-xl border border-[#26334D] bg-[#0A1020] px-4 py-3 font-mono text-xs leading-5 text-white outline-none focus:border-[#7C5CFC]" placeholder="{}" disabled={running || circuitOpen} /></label>}
        {simpleParameters && <button type="button" onClick={() => setUseAdvanced((current) => !current)} className="text-sm text-[#9B87FF] hover:text-white">{useAdvanced ? "Use generated form" : "Use advanced JSON arguments"}</button>}
      </div>

      <div className="mt-5 flex flex-wrap gap-2"><Button onClick={handleRun} disabled={running || circuitOpen}><Play size={16} />{running ? "Running..." : "Run Tool"}</Button>{result && <Link href="/audit"><Button variant="secondary">View Audit Log</Button></Link>}</div>
      {circuitOpen && <p className="mt-2 text-xs text-[#FCA5A5]">Disabled because the reliability circuit is open. Visit System Safety to reset it.</p>}
      {error && <p className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{error}</p>}

      {result && (
        <div className="mt-6 rounded-2xl border border-[#162036] bg-[#0A1020] p-4">
          <div className="flex flex-wrap items-center gap-2"><Badge variant={result.success ? "success" : "danger"}>{result.success ? "Success" : "Failure"}</Badge>{result.status && <Badge variant="default">{label(result.status)}</Badge>}</div>
          <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <Metric label="Execution ID" value={result.execution_id} />
            <Metric label="Started" value={formatDate(result.started_at)} />
            <Metric label="Completed" value={formatDate(result.completed_at)} />
            <Metric label="Duration" value={formatDuration(result.duration_ms)} />
          </div>
          <div className="mt-4"><h3 className="text-sm font-semibold text-[#CBD5E1]">Output</h3><pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap break-words rounded-xl bg-[#050A14] p-4 text-xs leading-5 text-[#94A3B8]">{formatJson(result.output)}</pre></div>
          {result.error && <p className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{result.error}{result.error_code ? ` (${result.error_code})` : ""}</p>}
          <details className="mt-4 rounded-xl border border-[#162036] bg-[#0D1321] p-3 text-sm"><summary className="cursor-pointer text-[#CBD5E1]">Technical details</summary><pre className="mt-3 max-h-52 overflow-auto whitespace-pre-wrap break-words text-xs leading-5 text-[#94A3B8]">{formatJson(result.metadata)}</pre></details>
        </div>
      )}
    </Card>
  );
}

function ParameterInput({ parameter, value, onChange, disabled }: { parameter: ToolParameterResponse; value: FieldValue; onChange: (value: FieldValue) => void; disabled: boolean }) {
  if (parameter.parameter_type === "boolean") {
    return <label className="flex items-start gap-3 rounded-xl border border-[#26334D] bg-[#0A1020] p-4 text-sm text-[#CBD5E1]"><input type="checkbox" checked={Boolean(value)} onChange={(event) => onChange(event.target.checked)} disabled={disabled} className="mt-1 accent-[#7C5CFC]" /><span><span className="font-medium">{parameter.name}{parameter.required ? " *" : ""}</span><span className="mt-1 block text-[#94A3B8]">{parameter.description || "Boolean value"}</span></span></label>;
  }

  const inputType = parameter.parameter_type === "integer" || parameter.parameter_type === "float" ? "number" : "text";
  return (
    <label className="block text-sm font-medium text-[#CBD5E1]">
      {parameter.name}{parameter.required ? " *" : ""}
      <span className="ml-2 font-normal text-[#64748B]">{label(parameter.parameter_type)}</span>
      {parameter.choices ? (
        <select value={String(value)} onChange={(event) => onChange(event.target.value)} disabled={disabled} className="mt-2 h-11 w-full rounded-xl border border-[#26334D] bg-[#0A1020] px-4 text-sm text-white outline-none focus:border-[#7C5CFC]"><option value="">Select...</option>{parameter.choices.map((choice) => <option key={String(choice)} value={String(choice)}>{String(choice)}</option>)}</select>
      ) : (
        <input type={inputType} step={parameter.parameter_type === "float" ? "any" : undefined} value={String(value)} onChange={(event) => onChange(event.target.value)} disabled={disabled} className="mt-2 h-11 w-full rounded-xl border border-[#26334D] bg-[#0A1020] px-4 text-sm text-white outline-none focus:border-[#7C5CFC]" />
      )}
      {parameter.description && <span className="mt-1 block text-xs font-normal text-[#94A3B8]">{parameter.description}</span>}
    </label>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="min-w-0 rounded-xl border border-[#162036] bg-[#0D1321] p-3"><p className="text-xs uppercase tracking-[0.14em] text-[#64748B]">{label}</p><p className="mt-2 truncate text-sm text-[#CBD5E1]" title={value}>{value}</p></div>;
}


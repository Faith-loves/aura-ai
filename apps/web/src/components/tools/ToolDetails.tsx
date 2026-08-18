"use client";

import Link from "next/link";
import { ArrowLeft, RefreshCw, ShieldAlert, Wrench } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import ToolExecutionPanel from "@/components/tools/ToolExecutionPanel";
import { formatJson, label, toolSafetyLabel } from "@/components/tools/tool-utils";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { getReliabilityStates } from "@/lib/api/safety";
import { getTools, searchTools } from "@/lib/api/tools";
import type { ReliabilityStateResponse, ToolResponse } from "@/types/api";

function safetyVariant(tool: ToolResponse) {
  if (tool.dangerous) return "danger";
  if (tool.requires_confirmation) return "warning";
  return "success";
}

function formatDate(value: string | null) {
  if (!value) return "Not available";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Unavailable" : date.toLocaleString();
}

export default function ToolDetails({ toolName }: { toolName: string }) {
  const decodedName = decodeURIComponent(toolName);
  const [tool, setTool] = useState<ToolResponse | null>(null);
  const [reliability, setReliability] = useState<ReliabilityStateResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTool = useCallback(async ({ refresh = false }: { refresh?: boolean } = {}) => {
    if (refresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      const [tools, reliabilityStates] = await Promise.all([getTools(), getReliabilityStates()]);
      const foundTool = tools.find((candidate) => candidate.name === decodedName) ?? (await searchTools(decodedName)).find((candidate) => candidate.name === decodedName) ?? null;
      if (!foundTool) throw new Error("Tool not found.");
      setTool(foundTool);
      setReliability(reliabilityStates);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to load tool details.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [decodedName]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadTool();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadTool]);

  const reliabilityState = useMemo(() => reliability.find((state) => state.tool_name === decodedName.toLowerCase() || state.tool_name === decodedName) ?? null, [decodedName, reliability]);

  if (loading) {
    return <Card className="mx-auto max-w-6xl p-6"><div className="h-6 w-64 animate-pulse rounded bg-[#1D2942]" /><div className="mt-6 h-96 animate-pulse rounded-2xl bg-[#1D2942]/50" /></Card>;
  }

  if (error || !tool) {
    return <Card className="mx-auto max-w-6xl p-6"><h1 className="text-xl font-semibold text-white">Tool details unavailable</h1><p className="mt-2 text-sm text-[#94A3B8]">{error ?? "Tool not found."}</p><Button className="mt-5" onClick={() => loadTool({ refresh: true })}>Retry</Button></Card>;
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <Link href="/tools" className="inline-flex items-center gap-2 text-sm text-[#94A3B8] transition hover:text-white"><ArrowLeft size={16} />Back to tools</Link>

      <section className="rounded-[20px] border border-[#1D2942] bg-[#0D1321]/78 p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2"><Badge variant={safetyVariant(tool)}>{toolSafetyLabel(tool)}</Badge><Badge variant="info">{label(tool.category)}</Badge><Badge variant="default">v{tool.version}</Badge></div>
            <h1 className="mt-4 flex items-center gap-3 text-3xl font-semibold tracking-tight text-white"><Wrench size={28} />{tool.name}</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-[#CBD5E1]">{tool.description}</p>
          </div>
          <Button variant="secondary" onClick={() => loadTool({ refresh: true })} disabled={refreshing}><RefreshCw size={16} className={refreshing ? "animate-spin" : ""} />Refresh</Button>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <Info label="Category" value={label(tool.category)} />
        <Info label="Version" value={tool.version} />
        <Info label="Parameters" value={String(tool.parameters.length)} />
      </section>

      {(tool.dangerous || tool.requires_confirmation) && <Card className="border-[#F59E0B]/35 p-5"><div className="flex gap-3 text-[#FCD34D]"><ShieldAlert size={20} /><div><h2 className="font-semibold">Extra care required</h2><p className="mt-1 text-sm text-[#FDE68A]">This tool is marked {tool.dangerous ? "dangerous" : "as requiring confirmation"} by the backend tool registry. Manual execution will ask for confirmation first.</p></div></div></Card>}

      <Card className="p-5 sm:p-6">
        <h2 className="text-lg font-semibold text-white">Parameters</h2>
        {tool.parameters.length === 0 ? <p className="mt-3 text-sm text-[#94A3B8]">This tool does not require parameters.</p> : (
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="text-xs uppercase tracking-[0.14em] text-[#64748B]"><tr><th className="px-3 py-2">Parameter</th><th className="px-3 py-2">Type</th><th className="px-3 py-2">Required</th><th className="px-3 py-2">Description</th><th className="px-3 py-2">Default</th></tr></thead>
              <tbody className="divide-y divide-[#162036] text-[#CBD5E1]">{tool.parameters.map((parameter) => <tr key={parameter.name}><td className="px-3 py-3 font-medium text-white">{parameter.name}</td><td className="px-3 py-3">{label(parameter.parameter_type)}</td><td className="px-3 py-3">{parameter.required ? "Yes" : "No"}</td><td className="px-3 py-3">{parameter.description || "—"}</td><td className="px-3 py-3">{parameter.default === null ? "—" : formatJson(parameter.default)}</td></tr>)}</tbody>
            </table>
          </div>
        )}
        <details className="mt-5 rounded-xl border border-[#162036] bg-[#0A1020] p-3 text-sm"><summary className="cursor-pointer text-[#CBD5E1]">Technical schema</summary><pre className="mt-3 max-h-80 overflow-auto whitespace-pre-wrap break-words text-xs leading-5 text-[#94A3B8]">{formatJson(tool.parameters)}</pre></details>
      </Card>

      <Card className="p-5 sm:p-6">
        <h2 className="text-lg font-semibold text-white">Reliability</h2>
        {reliabilityState ? <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-5"><Info label="Failures" value={String(reliabilityState.failure_count)} /><Info label="Successes" value={String(reliabilityState.success_count)} /><Info label="Circuit" value={reliabilityState.circuit_open ? "Open" : "Closed"} /><Info label="Last Failure" value={formatDate(reliabilityState.last_failure_at)} /><Info label="Last Error" value={reliabilityState.last_error ?? "None"} /></div> : <p className="mt-3 text-sm text-[#94A3B8]">No reliability state has been recorded for this tool yet.</p>}
        <Link href="/system" className="mt-4 inline-flex"><Button variant="secondary">View System Safety</Button></Link>
      </Card>

      <ToolExecutionPanel tool={tool} reliabilityState={reliabilityState} />
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return <div className="min-w-0 rounded-2xl border border-[#1D2942] bg-[#0D1321]/78 p-4"><p className="text-xs uppercase tracking-[0.14em] text-[#64748B]">{label}</p><p className="mt-2 truncate text-sm text-white" title={value}>{value}</p></div>;
}

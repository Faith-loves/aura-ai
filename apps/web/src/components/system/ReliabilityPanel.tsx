"use client";

import { RefreshCw, RotateCcw, ShieldAlert, ShieldCheck } from "lucide-react";
import { useState } from "react";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { resetReliabilityState } from "@/lib/api/safety";
import type { JsonValue, ReliabilityStateResponse } from "@/types/api";

function formatDate(value: string | null) {
  if (!value) return "Not available";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Unavailable" : date.toLocaleString();
}

function formatJson(value: Record<string, JsonValue>) {
  if (!value || Object.keys(value).length === 0) return "No metadata";
  return JSON.stringify(value, null, 2);
}

type ReliabilityPanelProps = {
  states: ReliabilityStateResponse[];
  loading?: boolean;
  error?: string | null;
  refreshing?: boolean;
  onRefresh: () => Promise<void> | void;
  onResetComplete: (state: ReliabilityStateResponse) => void;
};

export default function ReliabilityPanel({ states, loading = false, error = null, refreshing = false, onRefresh, onResetComplete }: ReliabilityPanelProps) {
  const [resettingTool, setResettingTool] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  async function handleReset(toolName: string) {
    const confirmed = window.confirm("Reset this tool's reliability state? This clears the current failure state but does not change its safety risk level.");
    if (!confirmed) return;

    setResettingTool(toolName);
    setActionError(null);

    try {
      const state = await resetReliabilityState(toolName);
      onResetComplete(state);
    } catch (nextError) {
      setActionError(nextError instanceof Error ? nextError.message : "Unable to reset reliability state.");
    } finally {
      setResettingTool(null);
    }
  }

  return (
    <Card className="p-5 sm:p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">Reliability</h2>
          <p className="mt-1 text-sm text-[#94A3B8]">Tracked tool health and circuit breaker state.</p>
        </div>
        <Button variant="secondary" onClick={onRefresh} disabled={refreshing} aria-label="Refresh reliability states"><RefreshCw size={16} className={refreshing ? "animate-spin" : ""} />Refresh</Button>
      </div>

      {actionError && <p className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{actionError}</p>}

      {loading ? (
        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {[0, 1].map((item) => <div key={item} className="h-44 animate-pulse rounded-2xl border border-[#162036] bg-[#0A1020]" />)}
        </div>
      ) : error ? (
        <div className="mt-5 rounded-2xl border border-[#EF4444]/30 bg-[#EF4444]/10 p-4"><h3 className="font-semibold text-[#FCA5A5]">Reliability data unavailable</h3><p className="mt-1 text-sm text-[#FECACA]">{error}</p><Button className="mt-4" variant="secondary" onClick={onRefresh}>Retry</Button></div>
      ) : states.length === 0 ? (
        <div className="mt-5 rounded-2xl border border-[#162036] bg-[#0A1020] p-6 text-center"><ShieldCheck size={30} className="mx-auto text-[#2DD4BF]" /><h3 className="mt-3 font-semibold text-white">No tracked reliability state</h3><p className="mt-1 text-sm text-[#94A3B8]">AURA has not recorded tool successes or failures in this runtime session.</p></div>
      ) : (
        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {states.map((state) => {
            const needsReset = state.circuit_open || state.failure_count > 0 || Boolean(state.last_error);
            return (
              <article key={state.tool_name} className="rounded-2xl border border-[#162036] bg-[#0A1020] p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0">
                    <h3 className="truncate text-lg font-semibold text-white">{state.tool_name}</h3>
                    <div className="mt-2 flex flex-wrap gap-2">
                      <Badge variant={state.circuit_open ? "danger" : "success"}>{state.circuit_open ? "Circuit Open" : "Healthy"}</Badge>
                    </div>
                  </div>
                  {needsReset && <Button variant="secondary" onClick={() => handleReset(state.tool_name)} disabled={resettingTool !== null}><RotateCcw size={15} className={resettingTool === state.tool_name ? "animate-spin" : ""} />Reset</Button>}
                </div>

                {state.circuit_open && <div className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 p-3 text-sm text-[#FCA5A5]"><div className="flex gap-2"><ShieldAlert size={17} /><p>AURA temporarily blocked this tool after repeated failures.</p></div></div>}

                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <Metric label="Failures" value={String(state.failure_count)} />
                  <Metric label="Successes" value={String(state.success_count)} />
                  <Metric label="Opened At" value={formatDate(state.opened_at)} />
                  <Metric label="Last Failure" value={formatDate(state.last_failure_at)} />
                  <Metric label="Last Success" value={formatDate(state.last_success_at)} />
                  <Metric label="Last Error" value={state.last_error ?? "None"} />
                </div>

                <details className="mt-4 rounded-xl border border-[#162036] bg-[#0D1321] p-3 text-sm">
                  <summary className="cursor-pointer text-[#CBD5E1]">Technical details</summary>
                  <pre className="mt-3 max-h-48 overflow-auto whitespace-pre-wrap break-words text-xs leading-5 text-[#94A3B8]">{formatJson(state.metadata)}</pre>
                </details>
              </article>
            );
          })}
        </div>
      )}
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="min-w-0 rounded-xl border border-[#162036] bg-[#0D1321] p-3"><p className="text-xs uppercase tracking-[0.14em] text-[#64748B]">{label}</p><p className="mt-2 truncate text-sm text-[#CBD5E1]" title={value}>{value}</p></div>;
}

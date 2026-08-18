"use client";

import Link from "next/link";
import { Activity, AlertTriangle, RefreshCw, Shield, ShieldCheck } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import ReliabilityPanel from "@/components/system/ReliabilityPanel";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { getHealth } from "@/lib/api/dashboard";
import { getApprovals, getAuditLog, getReliabilityStates, getSafetyPolicy } from "@/lib/api/safety";
import type { ApprovalResponse, AuditResponse, HealthResponse, JsonValue, ReliabilityStateResponse, SafetyPolicyResponse } from "@/types/api";

function formatPolicyName(name: string) {
  return name ? `${name.charAt(0).toUpperCase()}${name.slice(1)}` : "Unnamed";
}

function formatJson(value: Record<string, JsonValue>) {
  if (!value || Object.keys(value).length === 0) return "No metadata";
  return JSON.stringify(value, null, 2);
}

function policyRows(policy: SafetyPolicyResponse) {
  return [
    { label: "Low Risk", value: policy.allow_low_risk ? "Allowed" : "Blocked", safe: policy.allow_low_risk },
    { label: "Medium Risk", value: policy.allow_medium_risk ? "Allowed" : "Blocked", safe: policy.allow_medium_risk },
    { label: "High Risk", value: policy.require_approval_for_high_risk ? "Approval Required" : "Allowed without approval", safe: policy.require_approval_for_high_risk },
    { label: "Critical Risk", value: policy.block_critical_risk ? "Blocked" : "Allowed", safe: policy.block_critical_risk },
  ];
}

export default function SystemWorkspace() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [policy, setPolicy] = useState<SafetyPolicyResponse | null>(null);
  const [approvals, setApprovals] = useState<ApprovalResponse[]>([]);
  const [audit, setAudit] = useState<AuditResponse[]>([]);
  const [reliability, setReliability] = useState<ReliabilityStateResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [reliabilityLoading, setReliabilityLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [reliabilityRefreshing, setReliabilityRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reliabilityError, setReliabilityError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const loadReliability = useCallback(async ({ refresh = false }: { refresh?: boolean } = {}) => {
    if (refresh) setReliabilityRefreshing(true);
    else setReliabilityLoading(true);
    setReliabilityError(null);

    try {
      setReliability(await getReliabilityStates());
    } catch (nextError) {
      setReliabilityError(nextError instanceof Error ? nextError.message : "Unable to load reliability states.");
    } finally {
      setReliabilityLoading(false);
      setReliabilityRefreshing(false);
    }
  }, []);

  const loadOverview = useCallback(async ({ refresh = false }: { refresh?: boolean } = {}) => {
    if (refresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      const [nextHealth, nextPolicy, nextApprovals, nextAudit] = await Promise.all([getHealth(), getSafetyPolicy(), getApprovals(), getAuditLog()]);
      setHealth(nextHealth);
      setPolicy(nextPolicy);
      setApprovals(nextApprovals);
      setAudit(nextAudit);
      setLastUpdated(new Date());
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to load system safety overview.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadOverview();
      void loadReliability();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadOverview, loadReliability]);

  const summary = useMemo(() => {
    const pendingApprovals = approvals.filter((approval) => approval.status === "pending").length;
    const deniedActions = audit.filter((event) => event.event_type === "safety_denied" || event.event_type === "approval_rejected").length;
    const openCircuits = reliability.filter((state) => state.circuit_open).length;
    return { pendingApprovals, deniedActions, openCircuits };
  }, [approvals, audit, reliability]);

  async function refreshAll() {
    await Promise.all([loadOverview({ refresh: true }), loadReliability({ refresh: true })]);
  }

  function handleResetComplete(state: ReliabilityStateResponse) {
    setReliability((current) => {
      const exists = current.some((candidate) => candidate.tool_name === state.tool_name);
      return exists ? current.map((candidate) => candidate.tool_name === state.tool_name ? state : candidate) : [state, ...current];
    });
  }

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
      <section className="rounded-[20px] border border-[#1D2942] bg-[#0D1321]/78 p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <Badge variant="purple">AURA / System</Badge>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-[#F8FAFC]">System &amp; Safety</h1>
            <p className="mt-2 text-sm text-[#94A3B8]">Runtime protection and health.</p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <p className="text-xs text-[#64748B]">Last updated {lastUpdated ? lastUpdated.toLocaleTimeString() : "not yet"}</p>
            <Button variant="secondary" onClick={refreshAll} disabled={refreshing || reliabilityRefreshing} aria-label="Refresh system safety overview"><RefreshCw size={16} className={refreshing || reliabilityRefreshing ? "animate-spin" : ""} />Refresh</Button>
          </div>
        </div>
      </section>

      {error && <Card className="p-5"><h2 className="text-lg font-semibold text-white">System safety overview unavailable</h2><p className="mt-2 text-sm text-[#94A3B8]">{error}</p><Button className="mt-5" variant="secondary" onClick={() => loadOverview({ refresh: true })}>Retry</Button></Card>}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SummaryCard icon={<Shield size={20} />} label="Pending Approvals" value={loading ? "..." : String(summary.pendingApprovals)} tone={summary.pendingApprovals > 0 ? "warning" : "success"} href="/approvals" />
        <SummaryCard icon={<AlertTriangle size={20} />} label="Denied Actions" value={loading ? "..." : String(summary.deniedActions)} tone={summary.deniedActions > 0 ? "danger" : "success"} href="/audit" />
        <SummaryCard icon={<Activity size={20} />} label="Open Circuits" value={reliabilityLoading ? "..." : String(summary.openCircuits)} tone={summary.openCircuits > 0 ? "danger" : "success"} />
        <SummaryCard icon={<ShieldCheck size={20} />} label="Safety Policy" value={policy ? formatPolicyName(policy.name) : loading ? "..." : "Unavailable"} tone="purple" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_420px]">
        <Card className="p-5 sm:p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">Safety Policy</h2>
              <p className="mt-1 text-sm text-[#94A3B8]">Active policy rules exposed by the runtime.</p>
            </div>
            {policy && <Badge variant="purple">{formatPolicyName(policy.name)}</Badge>}
          </div>

          {loading ? (
            <div className="mt-5 space-y-3">{[0, 1, 2, 3].map((item) => <div key={item} className="h-14 animate-pulse rounded-xl bg-[#1D2942]/55" />)}</div>
          ) : policy ? (
            <>
              <div className="mt-5 space-y-3">
                {policyRows(policy).map((row) => (
                  <div key={row.label} className="flex items-center justify-between gap-4 rounded-xl border border-[#162036] bg-[#0A1020] p-4">
                    <span className="text-sm text-[#CBD5E1]">{row.label}</span>
                    <Badge variant={row.value === "Blocked" ? "danger" : row.value === "Approval Required" ? "warning" : "success"}>{row.value}</Badge>
                  </div>
                ))}
              </div>
              <details className="mt-4 rounded-xl border border-[#162036] bg-[#0A1020] p-3 text-sm">
                <summary className="cursor-pointer text-[#CBD5E1]">Policy metadata</summary>
                <pre className="mt-3 max-h-52 overflow-auto whitespace-pre-wrap break-words text-xs leading-5 text-[#94A3B8]">{formatJson(policy.metadata)}</pre>
              </details>
            </>
          ) : (
            <p className="mt-5 text-sm text-[#94A3B8]">Safety policy is unavailable.</p>
          )}
        </Card>

        <Card className="p-5 sm:p-6">
          <h2 className="text-lg font-semibold text-white">System Health</h2>
          <p className="mt-1 text-sm text-[#94A3B8]">Compact runtime status from the existing health endpoint.</p>
          {loading ? <div className="mt-5 h-44 animate-pulse rounded-2xl bg-[#1D2942]/50" /> : health ? (
            <div className="mt-5 space-y-3">
              <HealthRow label="API" value={health.status} good={health.status === "healthy"} />
              <HealthRow label="Kernel Ready" value={health.kernel.ready ? "Ready" : "Unavailable"} good={health.kernel.ready} />
              <HealthRow label="Model Provider" value={health.kernel.model_provider ?? "None"} good={health.kernel.model_provider_healthy} />
              <HealthRow label="Tools" value={String(health.kernel.tool_count)} good={health.kernel.tool_count > 0} />
            </div>
          ) : <p className="mt-5 text-sm text-[#94A3B8]">Health data is unavailable.</p>}
        </Card>
      </section>

      <ReliabilityPanel
        states={reliability}
        loading={reliabilityLoading}
        error={reliabilityError}
        refreshing={reliabilityRefreshing}
        onRefresh={() => loadReliability({ refresh: true })}
        onResetComplete={handleResetComplete}
      />

      <Card className="p-5 sm:p-6">
        <h2 className="text-lg font-semibold text-white">Runtime Protection</h2>
        <p className="mt-2 text-sm leading-6 text-[#94A3B8]">Reliability reset clears failure counters and circuit state for a tool. It does not change safety policy, risk classification, or whether a high-risk action requires approval.</p>
        <div className="mt-4 flex flex-wrap gap-2"><Link href="/approvals"><Button variant="secondary">Review Approvals</Button></Link><Link href="/audit"><Button variant="secondary">Open Audit Log</Button></Link></div>
      </Card>
    </div>
  );
}

function SummaryCard({ icon, label, value, tone, href }: { icon: ReactNode; label: string; value: string; tone: "success" | "warning" | "danger" | "purple"; href?: string }) {
  const content = <Card className="p-5"><div className="flex items-center justify-between gap-4"><div><p className="text-xs uppercase tracking-[0.14em] text-[#64748B]">{label}</p><p className="mt-2 text-2xl font-semibold text-white">{value}</p></div><Badge variant={tone}>{icon}</Badge></div></Card>;
  return href ? <Link href={href}>{content}</Link> : content;
}

function HealthRow({ label, value, good }: { label: string; value: string; good: boolean }) {
  return <div className="flex items-center justify-between gap-4 rounded-xl border border-[#162036] bg-[#0A1020] p-3"><span className="text-sm text-[#CBD5E1]">{label}</span><Badge variant={good ? "success" : "danger"}>{value}</Badge></div>;
}



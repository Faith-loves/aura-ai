"use client";

import Link from "next/link";
import { ArrowLeft, Check, ExternalLink, RefreshCw, ShieldAlert, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import ApprovalDecisionDialog from "@/components/safety/ApprovalDecisionDialog";
import ApprovalStatusBadge from "@/components/safety/ApprovalStatusBadge";
import RiskBadge from "@/components/safety/RiskBadge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { approveApproval, getApproval, rejectApproval } from "@/lib/api/safety";
import type { ApprovalDecisionRequest, ApprovalResponse, JsonValue } from "@/types/api";

function formatDate(value: string | null) {
  if (!value) return "Not available";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Unavailable" : date.toLocaleString();
}

function shortId(value: string | null) {
  if (!value) return "Not linked";
  return value.length > 16 ? `${value.slice(0, 10)}...${value.slice(-4)}` : value;
}

function formatJson(value: Record<string, JsonValue>) {
  if (!value || Object.keys(value).length === 0) return "No metadata";
  return JSON.stringify(value, null, 2);
}

export default function ApprovalDetails({ approvalId }: { approvalId: string }) {
  const [approval, setApproval] = useState<ApprovalResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [dialogMode, setDialogMode] = useState<"approve" | "reject" | null>(null);
  const [busyDecision, setBusyDecision] = useState(false);

  const loadApproval = useCallback(async ({ refresh = false }: { refresh?: boolean } = {}) => {
    if (refresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      setApproval(await getApproval(approvalId));
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to load approval.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [approvalId]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadApproval();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadApproval]);

  async function decide(mode: "approve" | "reject", request: ApprovalDecisionRequest) {
    setBusyDecision(true);
    setNotice(null);

    try {
      const nextApproval = mode === "approve" ? await approveApproval(approvalId, request) : await rejectApproval(approvalId, request);
      setApproval(nextApproval);
      setNotice(mode === "approve" ? "Approval granted. Return to the execution page if you want to continue runtime work." : "Approval rejected. AURA will keep this action blocked.");
      setDialogMode(null);
    } finally {
      setBusyDecision(false);
    }
  }

  if (loading) {
    return <Card className="mx-auto max-w-5xl p-6"><div className="h-6 w-64 animate-pulse rounded bg-[#1D2942]" /><div className="mt-6 h-96 animate-pulse rounded-2xl bg-[#1D2942]/50" /></Card>;
  }

  if (error || !approval) {
    return <Card className="mx-auto max-w-5xl p-6"><h1 className="text-xl font-semibold text-white">Approval unavailable</h1><p className="mt-2 text-sm text-[#94A3B8]">{error ?? "Approval not found."}</p><Button className="mt-5" onClick={() => loadApproval({ refresh: true })}>Retry</Button></Card>;
  }

  const pending = approval.status === "pending";

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <Link href="/approvals" className="inline-flex items-center gap-2 text-sm text-[#94A3B8] transition hover:text-white"><ArrowLeft size={16} />Back to approvals</Link>

      <section className="rounded-[20px] border border-[#1D2942] bg-[#0D1321]/78 p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2"><RiskBadge risk={approval.risk_level} /><ApprovalStatusBadge status={approval.status} /></div>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white">{approval.tool_name ?? "Approval request"}</h1>
            <p className="mt-2 text-sm leading-6 text-[#CBD5E1]">{approval.reason}</p>
            <p className="mt-3 truncate text-xs text-[#64748B]">Approval ID {approval.id}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => loadApproval({ refresh: true })} disabled={refreshing}><RefreshCw size={16} className={refreshing ? "animate-spin" : ""} />Refresh</Button>
            {pending && <Button variant="danger" onClick={() => setDialogMode("reject")} disabled={busyDecision}><X size={16} />Reject</Button>}
            {pending && <Button onClick={() => setDialogMode("approve")} disabled={busyDecision}><Check size={16} />Approve</Button>}
          </div>
        </div>

        {notice && (
          <div className="mt-5 rounded-2xl border border-[#22C55E]/30 bg-[#22C55E]/10 p-4 text-sm text-[#86EFAC]">
            {notice}
            {approval.execution_id && <Link href={`/executions/${approval.execution_id}`} className="ml-2 inline-flex items-center gap-1 text-white hover:text-[#C4B5FD]">View Execution <ExternalLink size={13} /></Link>}
          </div>
        )}
      </section>

      <div className="grid gap-4 md:grid-cols-2">
        <Info label="Requested At" value={formatDate(approval.requested_at)} />
        <Info label="Resolved At" value={formatDate(approval.resolved_at)} />
        <Info label="Resolved By" value={approval.resolved_by ?? "Not resolved"} />
        <Info label="Resolution Reason" value={approval.resolution_reason ?? "Not available"} />
        <Info label="Safety Decision" value={shortId(approval.safety_decision_id)} />
        <Info label="Step" value={shortId(approval.step_id)} />
      </div>

      <Card className="p-5 sm:p-6">
        <div className="flex items-start gap-3">
          <ShieldAlert size={22} className="mt-1 text-[#F59E0B]" />
          <div>
            <h2 className="text-lg font-semibold text-white">Runtime links</h2>
            <p className="mt-1 text-sm text-[#94A3B8]">Approval and execution resume are separate controls. This page records the safety decision only.</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {approval.execution_id && <Link href={`/executions/${approval.execution_id}`}><Button variant="secondary">View Execution</Button></Link>}
              {approval.plan_id && <Link href={`/plans/${approval.plan_id}`}><Button variant="secondary">View Plan</Button></Link>}
              {!approval.execution_id && !approval.plan_id && <span className="text-sm text-[#64748B]">No linked execution or plan.</span>}
            </div>
          </div>
        </div>
      </Card>

      <details className="rounded-2xl border border-[#1D2942] bg-[#0D1321]/78 p-5">
        <summary className="cursor-pointer text-sm font-medium text-[#CBD5E1]">Technical details</summary>
        <pre className="mt-4 max-h-80 overflow-auto whitespace-pre-wrap break-words rounded-xl bg-[#0A1020] p-4 text-xs leading-5 text-[#94A3B8]">{formatJson(approval.metadata)}</pre>
      </details>

      <ApprovalDecisionDialog
        open={dialogMode !== null}
        mode={dialogMode ?? "approve"}
        busy={busyDecision}
        onClose={() => setDialogMode(null)}
        onConfirm={(request) => dialogMode ? decide(dialogMode, request) : Promise.resolve()}
      />
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return <div className="min-w-0 rounded-2xl border border-[#1D2942] bg-[#0D1321]/78 p-4"><p className="text-xs uppercase tracking-[0.14em] text-[#64748B]">{label}</p><p className="mt-2 truncate text-sm text-[#F8FAFC]" title={value}>{value}</p></div>;
}

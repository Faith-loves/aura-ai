"use client";

import Link from "next/link";
import { AlertTriangle, CheckCircle2, ShieldAlert, XCircle } from "lucide-react";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { getCurrentStep, getExecutionProgress, isExecutionTerminal, titleCaseStatus } from "@/lib/executions/status";
import type { ExecutionResponse } from "@/types/api";

function metadataString(value: unknown) {
  return typeof value === "string" ? value : null;
}

function formatDuration(durationMs: number | null) {
  if (durationMs === null) return "Not available";
  const seconds = Math.max(0, Math.round(durationMs / 1000));
  const minutes = Math.floor(seconds / 60);
  return minutes > 0 ? `${minutes}m ${seconds % 60}s` : `${seconds}s`;
}

export function LiveMonitoringIndicator({ isMonitoring, monitoringUnavailable, terminal }: { isMonitoring: boolean; monitoringUnavailable: boolean; terminal: boolean }) {
  if (monitoringUnavailable) {
    return <Badge variant="warning">Monitoring unavailable</Badge>;
  }

  if (isMonitoring) {
    return <span className="inline-flex items-center gap-2 rounded-full border border-[#7C5CFC]/35 bg-[#7C5CFC]/12 px-3 py-1 text-xs font-medium text-[#C4B5FD]"><span className="h-2 w-2 animate-pulse rounded-full bg-[#2DD4BF]" />Live monitoring</span>;
  }

  return <Badge variant={terminal ? "success" : "default"}>{terminal ? "Monitoring complete" : "Monitoring idle"}</Badge>;
}

export default function ExecutionStatusPanel({ execution }: { execution: ExecutionResponse }) {
  const progress = getExecutionProgress(execution);
  const currentStep = getCurrentStep(execution);

  if (execution.status === "completed") {
    return <Card className="border-[#22C55E]/30 p-5"><div className="flex gap-3 text-[#86EFAC]"><CheckCircle2 size={22} /><div><h2 className="font-semibold">Execution completed</h2><p className="mt-1 text-sm text-[#BBF7D0]">{progress.completed} / {progress.total} steps completed. Duration {formatDuration(execution.duration_ms)}.</p></div></div></Card>;
  }

  if (execution.status === "cancelled") {
    return <Card className="border-[#64748B]/30 p-5"><div className="flex gap-3 text-[#CBD5E1]"><XCircle size={22} /><div><h2 className="font-semibold">Execution cancelled</h2><p className="mt-1 text-sm text-[#94A3B8]">AURA stopped this workflow before completion.</p></div></div></Card>;
  }

  if (execution.error_code === "approval_required") {
    const approvalId = currentStep ? metadataString(currentStep.metadata.approval_id) : null;
    return (
      <Card className="border-[#F59E0B]/35 p-5">
        <div className="flex items-start gap-3 text-[#FCD34D]"><ShieldAlert size={22} /><div><h2 className="font-semibold">Approval required</h2><p className="mt-1 text-sm text-[#FDE68A]">AURA paused before executing a high-risk action.</p>{approvalId && <p className="mt-2 text-xs text-[#FCD34D]">Approval ID {approvalId}</p>}<Link href={approvalId ? `/approvals?approval=${approvalId}` : "/approvals"}><Button className="mt-4" variant="secondary">Review Approval</Button></Link></div></div>
      </Card>
    );
  }

  if (execution.error_code === "reliability_circuit_open") {
    return <Card className="border-[#F59E0B]/35 p-5"><div className="flex gap-3 text-[#FCD34D]"><AlertTriangle size={22} /><div><h2 className="font-semibold">Tool temporarily blocked</h2><p className="mt-1 text-sm text-[#FDE68A]">AURA stopped the execution after repeated tool failures triggered reliability protection.</p><Link href="/system"><Button className="mt-4" variant="secondary">View Reliability</Button></Link></div></div></Card>;
  }

  if (execution.error_code === "authorization_denied") {
    return <Card className="border-[#EF4444]/35 p-5"><div className="flex gap-3 text-[#FCA5A5]"><ShieldAlert size={22} /><div><h2 className="font-semibold">Action blocked by safety policy</h2><p className="mt-1 text-sm text-[#FECACA]">{execution.error ?? "AURA denied this action under the active safety policy."}</p><div className="mt-4 flex flex-wrap gap-2"><Link href="/system"><Button variant="secondary">View Safety</Button></Link><Link href="/audit"><Button variant="secondary">View Audit</Button></Link></div></div></div></Card>;
  }

  if (execution.status === "failed") {
    return <Card className="border-[#EF4444]/35 p-5"><div className="flex gap-3 text-[#FCA5A5]"><XCircle size={22} /><div><h2 className="font-semibold">Execution failure</h2><p className="mt-1 text-sm text-[#FECACA]">{execution.error ?? "AURA reported an execution error."}</p>{execution.error_code && <p className="mt-2 text-xs text-[#FECACA]">Code: {execution.error_code}</p>}</div></div></Card>;
  }

  if (execution.status === "paused") {
    return <Card className="border-[#F59E0B]/30 p-5"><div className="flex gap-3 text-[#FCD34D]"><AlertTriangle size={22} /><div><h2 className="font-semibold">Execution paused</h2><p className="mt-1 text-sm text-[#FDE68A]">AURA is paused. Resume when the runtime state is ready.</p></div></div></Card>;
  }

  if (execution.status === "running") {
    return <Card className="border-[#7C5CFC]/35 p-5"><div className="flex gap-3 text-[#C4B5FD]"><span className="mt-1 h-3 w-3 animate-pulse rounded-full bg-[#2DD4BF]" /><div><h2 className="font-semibold">Execution running</h2><p className="mt-1 text-sm text-[#A5B4FC]">AURA is actively processing this workflow.</p></div></div></Card>;
  }

  if (!isExecutionTerminal(execution.status)) {
    return <Card className="p-5"><h2 className="font-semibold text-white">{titleCaseStatus(execution.status)}</h2><p className="mt-1 text-sm text-[#94A3B8]">Execution is waiting for the next runtime action.</p></Card>;
  }

  return null;
}

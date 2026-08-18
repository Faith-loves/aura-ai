"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Ban, Pause, Play, RefreshCw, RotateCcw, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import type { ReactNode } from "react";

import ElapsedTime from "@/components/executions/ElapsedTime";
import ExecutionStatusPanel, { LiveMonitoringIndicator } from "@/components/executions/ExecutionStatusPanel";
import { ExecutionActivityFeed, ExecutionTimeline } from "@/components/executions/ExecutionTimeline";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { useExecutionMonitor } from "@/hooks/useExecutionMonitor";
import { cancelExecution, deleteExecution, pauseExecution, resumeExecution, runExecution, startExecution } from "@/lib/api/executions";
import { getCurrentStep, getExecutionProgress, getNextVisibleStep, isExecutionTerminal, titleCaseStatus } from "@/lib/executions/status";
import type { ExecutionResponse, ExecutionStatus, StepExecutionResponse } from "@/types/api";

function badgeVariant(status: ExecutionStatus) {
  if (status === "completed") return "success";
  if (status === "failed" || status === "cancelled") return "danger";
  if (status === "running") return "info";
  if (status === "paused") return "warning";
  return "default";
}

function formatDate(value: string | null) {
  if (!value) return "Not available";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Unavailable" : date.toLocaleString();
}

function metadataString(step: StepExecutionResponse | null, key: string) {
  const value = step?.metadata[key];
  return typeof value === "string" ? value : null;
}

function metadataNumber(step: StepExecutionResponse | null, key: string) {
  const value = step?.metadata[key];
  return typeof value === "number" ? value : null;
}

function currentStepLabel(execution: ExecutionResponse, activeStep: StepExecutionResponse | null) {
  if (activeStep) return activeStep.title;
  if (execution.status === "pending") return "Waiting to start";
  if (execution.status === "completed") return "Complete";
  if (execution.status === "paused") return "No active step";
  return "No active step";
}

export default function ExecutionDetails({ executionId }: { executionId: string }) {
  const router = useRouter();
  const { data: execution, loading, error, refreshing, isMonitoring, monitoringUnavailable, lastUpdated, refresh, updateSnapshot } = useExecutionMonitor(executionId);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);

  const currentProgress = useMemo(() => execution ? getExecutionProgress(execution) : { total: 0, completed: 0, failed: 0, percent: 0 }, [execution]);
  const runningStep = execution ? getCurrentStep(execution) : null;
  const visibleStep = execution ? getNextVisibleStep(execution) : null;
  const activeStep = runningStep ?? visibleStep;
  const terminal = execution ? isExecutionTerminal(execution.status) : false;
  const canPause = execution?.status === "running" && !execution.current_step_id;
  const canResume = execution?.status === "paused" && execution.error_code !== "approval_required";

  async function runAction(labelText: string, action: () => Promise<ExecutionResponse>, confirmMessage?: string, optimisticStatus?: ExecutionStatus) {
    if (!execution) return;
    if (confirmMessage && !window.confirm(confirmMessage)) return;

    setBusyAction(labelText);
    setActionError(null);

    if (optimisticStatus) {
      updateSnapshot({
        ...execution,
        status: optimisticStatus,
        started_at: execution.started_at ?? new Date().toISOString(),
        error: optimisticStatus === "running" ? null : execution.error,
        error_code: optimisticStatus === "running" ? null : execution.error_code,
      });
    }

    try {
      const nextExecution = await action();
      updateSnapshot(nextExecution);
      void refresh({ refresh: true });
    } catch (nextError) {
      setActionError(nextError instanceof Error ? nextError.message : "Action failed.");
      void refresh({ refresh: true });
    } finally {
      setBusyAction(null);
    }
  }

  async function handleDelete() {
    if (!execution) return;
    if (!window.confirm("Delete this execution record?")) return;

    setBusyAction("delete");
    setActionError(null);

    try {
      await deleteExecution(execution.id);
      router.push("/executions");
    } catch (nextError) {
      setActionError(nextError instanceof Error ? nextError.message : "Unable to delete execution.");
      setBusyAction(null);
    }
  }

  if (loading && !execution) {
    return <Card className="mx-auto max-w-6xl p-6"><div className="h-6 w-64 animate-pulse rounded bg-[#1D2942]/60" /><div className="mt-5 h-72 animate-pulse rounded-2xl bg-[#1D2942]/40" /></Card>;
  }

  if (error && !execution) {
    return <Card className="mx-auto max-w-6xl p-6"><h1 className="text-xl font-semibold text-white">Execution unavailable</h1><p className="mt-2 text-sm text-[#94A3B8]">{error}</p><Button className="mt-5" onClick={() => refresh({ refresh: true })}>Retry</Button></Card>;
  }

  if (!execution) return null;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6" aria-live="polite">
      <Link href="/executions" className="inline-flex items-center gap-2 text-sm text-[#94A3B8] transition hover:text-white"><ArrowLeft size={16} />Back to executions</Link>

      <section className="rounded-[20px] border border-[#1D2942] bg-[#0D1321]/78 p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={badgeVariant(execution.status)}>{titleCaseStatus(execution.status)}</Badge>
              <LiveMonitoringIndicator isMonitoring={isMonitoring} monitoringUnavailable={monitoringUnavailable} terminal={terminal} />
              {refreshing && <Badge variant="default">Refreshing</Badge>}
            </div>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white">{execution.goal}</h1>
            <p className="mt-2 truncate text-xs text-[#64748B]">Execution ID {execution.id}</p>
            <p className="mt-1 truncate text-xs text-[#64748B]">Plan <Link href={`/plans/${execution.plan_id}`} className="text-[#9B87FF] hover:text-white">{execution.plan_id}</Link></p>
            <p className="mt-2 text-xs text-[#64748B]">Last updated {lastUpdated ? lastUpdated.toLocaleTimeString() : "not yet"}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => refresh({ refresh: true })} disabled={refreshing}><RefreshCw size={16} className={refreshing ? "animate-spin" : ""} />Refresh</Button>
            {execution.status === "pending" && <Button onClick={() => runAction("start", () => startExecution(execution.id), undefined, "running")} disabled={busyAction !== null}><Play size={16} />{busyAction === "start" ? "Starting..." : "Start"}</Button>}
            {(execution.status === "pending" || execution.status === "running") && <Button onClick={() => runAction("run", () => runExecution(execution.id), undefined, "running")} disabled={busyAction !== null}><RotateCcw size={16} className={busyAction === "run" ? "animate-spin" : ""} />{busyAction === "run" ? "Running..." : "Run"}</Button>}
            {canPause && <Button variant="secondary" onClick={() => runAction("pause", () => pauseExecution(execution.id))} disabled={busyAction !== null}><Pause size={16} />Pause</Button>}
            {canResume && <Button onClick={() => runAction("resume", () => resumeExecution(execution.id), undefined, "running")} disabled={busyAction !== null}><Play size={16} />Resume</Button>}
            {!terminal && <Button variant="danger" onClick={() => runAction("cancel", () => cancelExecution(execution.id), "Cancel this execution?", "cancelled")} disabled={busyAction !== null}><Ban size={16} />Cancel</Button>}
            <Button variant="danger" onClick={handleDelete} disabled={busyAction !== null}><Trash2 size={16} />Delete</Button>
          </div>
        </div>

        {error && execution && <p className="mt-4 rounded-xl border border-[#F59E0B]/30 bg-[#F59E0B]/10 px-3 py-2 text-sm text-[#FCD34D]">Connection interrupted. Keeping the last successful execution state visible. {monitoringUnavailable ? "Use Retry to reconnect." : "AURA will retry on the next polling interval."}</p>}
        {actionError && <p className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{actionError}</p>}

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Info label="Progress" value={`${currentProgress.percent}% · ${currentProgress.completed} / ${currentProgress.total} steps`} />
          <Info label="Current Step" value={currentStepLabel(execution, activeStep)} />
          <Info label="Elapsed" valueNode={<ElapsedTime startedAt={execution.started_at} completedAt={execution.completed_at} durationMs={execution.duration_ms} running={execution.status === "running"} />} />
          <Info label="Started" value={formatDate(execution.started_at)} />
        </div>
        <div className="mt-5 h-2 overflow-hidden rounded-full bg-[#162036]"><div className="h-full rounded-full bg-gradient-to-r from-[#7C5CFC] to-[#2DD4BF] shadow-[0_0_18px_rgba(124,92,252,0.28)]" style={{ width: `${currentProgress.percent}%` }} /></div>
      </section>

      <ExecutionStatusPanel execution={execution} />
      <CurrentStepPanel execution={execution} step={activeStep} runningStep={runningStep} />
      <ExecutionTimeline execution={execution} />
      <ExecutionActivityFeed execution={execution} />
    </div>
  );
}

function Info({ label, value, valueNode }: { label: string; value?: string; valueNode?: ReactNode }) {
  return <div className="rounded-xl border border-[#162036] bg-[#0A1020] p-4"><p className="text-xs uppercase tracking-[0.14em] text-[#64748B]">{label}</p><p className="mt-2 truncate text-sm font-medium text-[#F8FAFC]">{valueNode ?? value}</p></div>;
}

function CurrentStepPanel({ execution, step, runningStep }: { execution: ExecutionResponse; step: StepExecutionResponse | null; runningStep: StepExecutionResponse | null }) {
  return (
    <Card className="p-5 sm:p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <h2 className="text-lg font-semibold text-white">Current Step</h2>
          <p className="mt-2 text-xl font-semibold text-[#F8FAFC]">{currentStepLabel(execution, step)}</p>
          {step && <p className="mt-1 text-sm text-[#94A3B8]">Status: {titleCaseStatus(step.status)}</p>}
          {!step && <p className="mt-1 text-sm text-[#94A3B8]">{execution.status === "pending" ? "Waiting to start." : "No active step is currently reported by the runtime."}</p>}
        </div>
        {runningStep && <span className="inline-flex items-center gap-2 rounded-full border border-[#7C5CFC]/35 bg-[#7C5CFC]/12 px-3 py-1 text-xs font-medium text-[#C4B5FD]"><span className="h-2 w-2 animate-pulse rounded-full bg-[#2DD4BF]" />Running</span>}
      </div>
      {step && <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-5"><Info label="Tool" value={step.tool_name ?? "Unbound"} /><Info label="Attempt" value={String(metadataNumber(step, "attempt_count") ?? "None")} /><Info label="Risk" value={metadataString(step, "risk_level") ? titleCaseStatus(metadataString(step, "risk_level") ?? "") : "Not evaluated"} /><Info label="Safety" value={metadataString(step, "permission_decision") ? titleCaseStatus(metadataString(step, "permission_decision") ?? "") : "Not evaluated"} /><Info label="Approval" value={metadataString(step, "approval_status") ? titleCaseStatus(metadataString(step, "approval_status") ?? "") : "Not required"} /></div>}
    </Card>
  );
}


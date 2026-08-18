"use client";

import { Activity, CheckCircle2, Circle, CircleDot, MinusCircle, XCircle } from "lucide-react";

import Badge from "@/components/ui/Badge";
import Card from "@/components/ui/Card";
import { getCurrentStep, titleCaseStatus } from "@/lib/executions/status";
import type { ExecutionResponse, JsonValue, StepExecutionResponse, StepExecutionStatus } from "@/types/api";

function badgeVariant(status: StepExecutionStatus) {
  if (status === "completed" || status === "skipped") return "success";
  if (status === "failed") return "danger";
  if (status === "running" || status === "ready") return "info";
  return "default";
}

function StepIcon({ status }: { status: StepExecutionStatus }) {
  if (status === "completed") return <CheckCircle2 size={18} className="text-[#22C55E]" />;
  if (status === "skipped") return <MinusCircle size={18} className="text-[#94A3B8]" />;
  if (status === "failed") return <XCircle size={18} className="text-[#EF4444]" />;
  if (status === "running") return <Activity size={18} className="animate-pulse text-[#7C5CFC]" />;
  if (status === "ready") return <CircleDot size={18} className="text-[#2DD4BF]" />;
  return <Circle size={18} className="text-[#64748B]" />;
}

function formatDate(value: string | null) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function formatDuration(durationMs: number | null) {
  if (durationMs === null) return null;
  const seconds = Math.max(0, Math.round(durationMs / 1000));
  const minutes = Math.floor(seconds / 60);
  return minutes > 0 ? `${minutes}m ${seconds % 60}s` : `${seconds}s`;
}

function summarizeJson(value: JsonValue | undefined) {
  if (value === undefined || value === null) return "None";
  if (typeof value === "string") return value;
  return JSON.stringify(value, null, 2);
}

function metadataString(step: StepExecutionResponse, key: string) {
  const value = step.metadata[key];
  return typeof value === "string" ? value : null;
}

function operationalChips(step: StepExecutionResponse) {
  const chips: string[] = [];
  if (step.tool_name) chips.push(`Tool ${step.tool_name}`);
  if (typeof step.metadata.attempt_count === "number") chips.push(`Attempt ${step.metadata.attempt_count}`);
  const risk = metadataString(step, "risk_level");
  if (risk) chips.push(`Risk ${titleCaseStatus(risk)}`);
  const decision = metadataString(step, "permission_decision");
  if (decision) chips.push(`Safety ${titleCaseStatus(decision)}`);
  const approval = metadataString(step, "approval_status");
  if (approval) chips.push(`Approval ${titleCaseStatus(approval)}`);
  if (typeof step.metadata.reliability_failure_count === "number") chips.push(`Failures ${step.metadata.reliability_failure_count}`);
  if (typeof step.metadata.circuit_open === "boolean") chips.push(`Circuit ${step.metadata.circuit_open ? "Open" : "Closed"}`);
  return chips;
}

export function ExecutionTimeline({ execution }: { execution: ExecutionResponse }) {
  return (
    <Card className="p-5 sm:p-6">
      <h2 className="text-lg font-semibold text-white">Workflow</h2>
      <div className="mt-5 space-y-4">
        {execution.step_executions.map((step, index) => <StepExecutionCard key={step.id} step={step} index={index} />)}
      </div>
    </Card>
  );
}

function StepExecutionCard({ step, index }: { step: StepExecutionResponse; index: number }) {
  const chips = operationalChips(step);
  const startedAt = formatDate(step.started_at);
  const completedAt = formatDate(step.completed_at);
  const duration = formatDuration(step.duration_ms);

  return (
    <article className="rounded-2xl border border-[#162036] bg-[#0A1020]/80 p-4" aria-label={`Step ${index + 1}: ${step.title}, ${titleCaseStatus(step.status)}`}>
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 gap-3">
          <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[#26334D] bg-[#111A2E]"><StepIcon status={step.status} /></div>
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-[0.14em] text-[#64748B]">Step {index + 1}</p>
            <h3 className="mt-1 text-base font-semibold text-white">{step.title}</h3>
            {step.status === "running" && <p className="mt-2 inline-flex items-center gap-2 text-sm text-[#C4B5FD]"><span className="h-2 w-2 animate-pulse rounded-full bg-[#2DD4BF]" />Running</p>}
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-[#94A3B8]">{chips.map((chip) => <span key={chip} className="rounded-full bg-[#111A2E] px-2.5 py-1">{chip}</span>)}</div>
            <div className="mt-3 flex flex-wrap gap-3 text-xs text-[#64748B]">{startedAt && <span>Started {startedAt}</span>}{completedAt && <span>Completed {completedAt}</span>}{duration && <span>Duration {duration}</span>}</div>
          </div>
        </div>
        <Badge variant={badgeVariant(step.status)}>{titleCaseStatus(step.status)}</Badge>
      </div>

      {step.error && <p className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">Error: {step.error}{step.error_code ? ` (${step.error_code})` : ""}</p>}

      <div className="mt-4 grid gap-3 lg:grid-cols-3">
        <Disclosure title="Arguments" value={step.arguments} />
        <Disclosure title="View output" value={step.output} />
        <Disclosure title="Technical details" value={step.metadata} />
      </div>
    </article>
  );
}

function Disclosure({ title, value }: { title: string; value: JsonValue | undefined }) {
  return (
    <details className="rounded-xl border border-[#162036] bg-[#0D1321] p-3 text-sm">
      <summary className="cursor-pointer text-[#CBD5E1]">{title}</summary>
      <pre className="mt-3 max-h-48 overflow-auto whitespace-pre-wrap break-words text-xs leading-5 text-[#94A3B8]">{summarizeJson(value)}</pre>
    </details>
  );
}

export function ExecutionActivityFeed({ execution }: { execution: ExecutionResponse }) {
  const currentStep = getCurrentStep(execution);
  const events = buildActivityEvents(execution, currentStep);

  return (
    <Card className="p-5 sm:p-6">
      <h2 className="text-lg font-semibold text-white">Activity</h2>
      <div className="mt-5 space-y-3">
        {events.map((event, index) => (
          <div key={`${event.label}-${index}`} className="flex gap-3 text-sm">
            <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-[#7C5CFC]" />
            <div className="min-w-0"><p className="text-[#CBD5E1]">{event.label}</p>{event.time && <p className="mt-1 text-xs text-[#64748B]">{event.time}</p>}</div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function buildActivityEvents(execution: ExecutionResponse, currentStep: StepExecutionResponse | null) {
  const events: { label: string; time: string | null }[] = [];
  if (execution.started_at) events.push({ label: "Execution started", time: formatDate(execution.started_at) });

  for (const step of execution.step_executions) {
    if (step.status === "running") events.push({ label: `Step running: ${step.title}`, time: formatDate(step.started_at) });
    if (step.status === "completed") events.push({ label: `Step completed: ${step.title}`, time: formatDate(step.completed_at) });
    if (step.status === "skipped") events.push({ label: `Step skipped: ${step.title}`, time: formatDate(step.completed_at) });
    if (step.status === "failed") events.push({ label: `Step failed: ${step.title}`, time: formatDate(step.completed_at) });
  }

  if (execution.error_code === "approval_required") events.push({ label: "Approval required", time: currentStep ? formatDate(currentStep.started_at) : null });
  if (execution.status === "completed") events.push({ label: "Execution completed", time: formatDate(execution.completed_at) });
  if (execution.status === "failed") events.push({ label: "Execution failed", time: formatDate(execution.completed_at) });
  if (execution.status === "cancelled") events.push({ label: "Execution cancelled", time: formatDate(execution.completed_at) });

  return events.length > 0 ? events.slice(-8).reverse() : [{ label: "Waiting to start", time: null }];
}

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, CheckCircle2, Circle, CircleDot, Flag, RefreshCw, Trash2, XCircle } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { completePlan, completePlanStep, deletePlan, getPlan, startPlan, startPlanStep, updateStepPriority } from "@/lib/api/plans";
import type { PlanResponse, PlanStatus, PlanStepResponse, PlanStepStatus } from "@/types/api";

function label(status: string) {
  return status.split("_").map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`).join(" ");
}

function planBadge(status: PlanStatus) {
  if (status === "completed") return "success";
  if (status === "failed" || status === "cancelled") return "danger";
  if (status === "in_progress") return "info";
  return "purple";
}

function stepBadge(status: PlanStepStatus) {
  if (status === "completed" || status === "skipped") return "success";
  if (status === "failed") return "danger";
  if (status === "in_progress" || status === "ready") return "info";
  return "default";
}

function StepIcon({ status }: { status: PlanStepStatus }) {
  if (status === "completed" || status === "skipped") return <CheckCircle2 size={18} className="text-[#22C55E]" />;
  if (status === "failed") return <XCircle size={18} className="text-[#EF4444]" />;
  if (status === "in_progress" || status === "ready") return <CircleDot size={18} className="text-[#2DD4BF]" />;
  return <Circle size={18} className="text-[#64748B]" />;
}

function progress(plan: PlanResponse) {
  const total = plan.steps.length;
  const complete = plan.steps.filter((step) => ["completed", "skipped"].includes(step.status)).length;
  return { total, complete, percent: total > 0 ? Math.round((complete / total) * 100) : 0 };
}

function dependencyLabel(stepId: string, steps: PlanStepResponse[]) {
  const index = steps.findIndex((step) => step.id === stepId);
  if (index < 0) return stepId;
  return `Step ${index + 1}: ${steps[index].title}`;
}

export default function PlanDetails({ planId }: { planId: string }) {
  const router = useRouter();
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);

  const loadPlan = useCallback(async ({ refresh = false }: { refresh?: boolean } = {}) => {
    if (refresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      setPlan(await getPlan(planId));
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to load plan.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [planId]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadPlan();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadPlan]);

  const progressValue = useMemo(() => plan ? progress(plan) : { total: 0, complete: 0, percent: 0 }, [plan]);
  const canComplete = plan?.status === "in_progress" && plan.steps.every((step) => ["completed", "skipped"].includes(step.status));

  async function runAction(labelText: string, action: () => Promise<PlanResponse>) {
    setBusyAction(labelText);
    setActionError(null);

    try {
      setPlan(await action());
    } catch (nextError) {
      setActionError(nextError instanceof Error ? nextError.message : "Action failed.");
    } finally {
      setBusyAction(null);
    }
  }

  async function handleDelete() {
    if (!plan) return;
    const confirmed = window.confirm("Delete this plan? This action removes the plan record.");
    if (!confirmed) return;

    setBusyAction("delete-plan");
    setActionError(null);

    try {
      await deletePlan(plan.id);
      router.push("/plans");
    } catch (nextError) {
      setActionError(nextError instanceof Error ? nextError.message : "Unable to delete plan.");
      setBusyAction(null);
    }
  }

  if (loading) {
    return <Card className="mx-auto max-w-6xl p-6"><div className="h-6 w-52 animate-pulse rounded bg-[#1D2942]/60" /><div className="mt-5 h-64 animate-pulse rounded-2xl bg-[#1D2942]/40" /></Card>;
  }

  if (error || !plan) {
    return <Card className="mx-auto max-w-6xl p-6"><h1 className="text-xl font-semibold text-white">Plan unavailable</h1><p className="mt-2 text-sm text-[#94A3B8]">{error ?? "Plan not found."}</p><Button className="mt-5" onClick={() => loadPlan({ refresh: true })}>Retry</Button></Card>;
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <Link href="/plans" className="inline-flex items-center gap-2 text-sm text-[#94A3B8] transition hover:text-white"><ArrowLeft size={16} />Back to plans</Link>

      <section className="rounded-[20px] border border-[#1D2942] bg-[#0D1321]/78 p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <Badge variant={planBadge(plan.status)}>{label(plan.status)}</Badge>
            <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white">{plan.goal}</h1>
            <p className="mt-2 truncate text-xs text-[#64748B]">Plan ID {plan.id}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => loadPlan({ refresh: true })} disabled={refreshing}><RefreshCw size={16} className={refreshing ? "animate-spin" : ""} />Refresh</Button>
            {plan.status === "pending" && <Button onClick={() => runAction("start-plan", () => startPlan(plan.id))} disabled={busyAction !== null}><Flag size={16} />Start Plan</Button>}
            {canComplete && <Button onClick={() => runAction("complete-plan", () => completePlan(plan.id))} disabled={busyAction !== null}><CheckCircle2 size={16} />Complete Plan</Button>}
            <Button variant="danger" onClick={handleDelete} disabled={busyAction !== null}><Trash2 size={16} />Delete Plan</Button>
          </div>
        </div>
        <div className="mt-6">
          <div className="mb-2 flex justify-between text-xs text-[#94A3B8]"><span>{progressValue.complete} / {progressValue.total} complete</span><span>{progressValue.percent}%</span></div>
          <div className="h-2 overflow-hidden rounded-full bg-[#162036]"><div className="h-full rounded-full bg-gradient-to-r from-[#7C5CFC] to-[#2DD4BF]" style={{ width: `${progressValue.percent}%` }} /></div>
        </div>
        {actionError && <p className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{actionError}</p>}
      </section>

      <Card className="p-5 sm:p-6">
        <h2 className="text-lg font-semibold text-white">Workflow</h2>
        <div className="mt-5 space-y-4">
          {plan.steps.map((step, index) => (
            <div key={step.id} className="rounded-2xl border border-[#162036] bg-[#0A1020]/80 p-4">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="flex gap-3">
                  <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[#26334D] bg-[#111A2E]"><StepIcon status={step.status} /></div>
                  <div>
                    <p className="text-xs font-medium uppercase tracking-[0.14em] text-[#64748B]">Step {index + 1}</p>
                    <h3 className="mt-1 text-base font-semibold text-white">{step.title}</h3>
                    {step.description && <p className="mt-2 text-sm leading-6 text-[#94A3B8]">{step.description}</p>}
                    {step.dependencies.length > 0 && <p className="mt-3 text-xs text-[#64748B]">Depends on: {step.dependencies.map((dependency) => dependencyLabel(dependency, plan.steps)).join(", ")}</p>}
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-2 lg:justify-end">
                  <Badge variant={stepBadge(step.status)}>{label(step.status)}</Badge>
                  <label className="flex items-center gap-2 rounded-xl border border-[#26334D] bg-[#111A2E] px-3 py-2 text-xs text-[#94A3B8]">
                    Priority
                    <select
                      value={step.priority}
                      disabled={busyAction !== null}
                      onChange={(event) => runAction(`priority-${step.id}`, () => updateStepPriority(plan.id, step.id, Number(event.target.value)))}
                      className="bg-transparent text-[#F8FAFC] outline-none"
                    >
                      {[1, 2, 3, 4, 5].map((priority) => <option key={priority} value={priority}> {priority}</option>)}
                    </select>
                  </label>
                  {step.status === "ready" && <Button className="h-9" onClick={() => runAction(`start-${step.id}`, () => startPlanStep(plan.id, step.id))} disabled={busyAction !== null}>Start</Button>}
                  {step.status === "in_progress" && <Button className="h-9" onClick={() => runAction(`complete-${step.id}`, () => completePlanStep(plan.id, step.id))} disabled={busyAction !== null}>Complete</Button>}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}



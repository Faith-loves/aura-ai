"use client";

import { X } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import Button from "@/components/ui/Button";
import { createExecution } from "@/lib/api/executions";
import { getPlans } from "@/lib/api/plans";
import type { ExecutionResponse, PlanResponse } from "@/types/api";

type CreateExecutionDialogProps = {
  open: boolean;
  onClose: () => void;
  onCreated: (execution: ExecutionResponse) => void;
};

export default function CreateExecutionDialog({ open, onClose, onCreated }: CreateExecutionDialogProps) {
  const [plans, setPlans] = useState<PlanResponse[]>([]);
  const [planId, setPlanId] = useState("");
  const [loadingPlans, setLoadingPlans] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;

    let cancelled = false;
    const timeoutId = window.setTimeout(() => {
      setLoadingPlans(true);
      setError(null);

      getPlans()
        .then((nextPlans) => {
          if (cancelled) return;
          const eligible = nextPlans.filter((plan) => plan.steps.length > 0 && !["completed", "failed", "cancelled"].includes(plan.status));
          setPlans(eligible);
          setPlanId(eligible[0]?.id ?? "");
        })
        .catch((nextError) => {
          if (!cancelled) setError(nextError instanceof Error ? nextError.message : "Unable to load plans.");
        })
        .finally(() => {
          if (!cancelled) setLoadingPlans(false);
        });
    }, 0);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [open]);

  if (!open) return null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!planId || submitting) return;

    setSubmitting(true);
    setError(null);

    try {
      const execution = await createExecution({ plan_id: planId });
      onCreated(execution);
      onClose();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to create execution.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="create-execution-title">
      <div className="w-full max-w-xl rounded-2xl border border-[#1D2942] bg-[#0D1321] p-5 shadow-2xl shadow-black/35">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 id="create-execution-title" className="text-lg font-semibold text-[#F8FAFC]">New Execution</h2>
            <p className="mt-1 text-sm text-[#94A3B8]">Create an autonomous run from an existing plan.</p>
          </div>
          <button type="button" onClick={onClose} aria-label="Close new execution dialog" className="rounded-lg p-2 text-[#64748B] transition hover:bg-white/[0.05] hover:text-white"><X size={18} /></button>
        </div>

        <form onSubmit={handleSubmit} className="mt-5">
          <label htmlFor="execution-plan" className="text-sm font-medium text-[#CBD5E1]">Plan</label>
          <select
            id="execution-plan"
            value={planId}
            onChange={(event) => setPlanId(event.target.value)}
            disabled={loadingPlans || plans.length === 0}
            className="mt-2 h-11 w-full rounded-xl border border-[#162036] bg-[#0A1020] px-3 text-sm text-[#F8FAFC] outline-none transition focus:border-[#7C5CFC]/60"
          >
            {plans.length === 0 ? <option value="">No eligible plans</option> : plans.map((plan) => <option key={plan.id} value={plan.id}>{plan.goal}</option>)}
          </select>
          <p className="mt-2 text-xs text-[#64748B]">Eligible plans are pending or in progress and contain at least one step.</p>

          {error && <p className="mt-3 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{error}</p>}

          <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="ghost" onClick={onClose} disabled={submitting}>Cancel</Button>
            <Button type="submit" disabled={!planId || submitting || loadingPlans}>{submitting ? "Creating..." : "Create Execution"}</Button>
          </div>
        </form>
      </div>
    </div>
  );
}


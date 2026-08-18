"use client";

import { X } from "lucide-react";
import { FormEvent, useState } from "react";

import Button from "@/components/ui/Button";
import { createPlan } from "@/lib/api/plans";
import type { PlanResponse } from "@/types/api";

type CreatePlanDialogProps = {
  open: boolean;
  onClose: () => void;
  onCreated: (plan: PlanResponse) => void;
};

export default function CreatePlanDialog({ open, onClose, onCreated }: CreatePlanDialogProps) {
  const [goal, setGoal] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) {
    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedGoal = goal.trim();

    if (!trimmedGoal || submitting) {
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const plan = await createPlan({ goal: trimmedGoal });
      setGoal("");
      onCreated(plan);
      onClose();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to create plan.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="create-plan-title">
      <div className="w-full max-w-xl rounded-2xl border border-[#1D2942] bg-[#0D1321] p-5 shadow-2xl shadow-black/35">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 id="create-plan-title" className="text-lg font-semibold text-[#F8FAFC]">Create Plan</h2>
            <p className="mt-1 text-sm text-[#94A3B8]">Turn a goal into structured executable steps.</p>
          </div>
          <button type="button" onClick={onClose} aria-label="Close create plan dialog" className="rounded-lg p-2 text-[#64748B] transition hover:bg-white/[0.05] hover:text-white">
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-5">
          <label htmlFor="plan-goal" className="text-sm font-medium text-[#CBD5E1]">Goal</label>
          <textarea
            id="plan-goal"
            value={goal}
            onChange={(event) => setGoal(event.target.value)}
            rows={5}
            placeholder="Describe the goal AURA should create a plan for..."
            className="mt-2 min-h-32 w-full resize-none rounded-xl border border-[#162036] bg-[#0A1020] px-4 py-3 text-sm leading-6 text-[#F8FAFC] outline-none transition placeholder:text-[#64748B] focus:border-[#7C5CFC]/60"
          />

          {error && <p className="mt-3 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{error}</p>}

          <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="ghost" onClick={onClose} disabled={submitting}>Cancel</Button>
            <Button type="submit" disabled={!goal.trim() || submitting}>{submitting ? "Creating..." : "Create Plan"}</Button>
          </div>
        </form>
      </div>
    </div>
  );
}

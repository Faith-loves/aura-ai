"use client";

import { useId, useState } from "react";

import Button from "@/components/ui/Button";
import type { ApprovalDecisionRequest } from "@/types/api";

type ApprovalDecisionDialogProps = {
  open: boolean;
  mode: "approve" | "reject";
  busy?: boolean;
  onClose: () => void;
  onConfirm: (request: ApprovalDecisionRequest) => Promise<void>;
};

export default function ApprovalDecisionDialog({ open, mode, busy = false, onClose, onConfirm }: ApprovalDecisionDialogProps) {
  const titleId = useId();
  const [resolvedBy, setResolvedBy] = useState("");
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);


  if (!open) return null;

  function resetForm() {
    setResolvedBy("");
    setReason("");
    setError(null);
  }

  function handleClose() {
    resetForm();
    onClose();
  }

  async function handleConfirm() {
    setError(null);

    try {
      await onConfirm({
        resolved_by: resolvedBy.trim() || null,
        reason: reason.trim() || null,
      });
      resetForm();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to submit decision.");
    }
  }

  const approving = mode === "approve";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4" role="dialog" aria-modal="true" aria-labelledby={titleId}>
      <div className="w-full max-w-lg rounded-[22px] border border-[#26334D] bg-[#0D1321] p-6 shadow-2xl shadow-black/50">
        <h2 id={titleId} className="text-xl font-semibold text-white">{approving ? "Approve action" : "Reject action"}</h2>
        <p className="mt-2 text-sm leading-6 text-[#94A3B8]">
          {approving
            ? "This records approval for the paused safety request. It does not automatically resume an execution from this page."
            : "This records a rejection for the paused safety request. AURA will keep the action blocked under this decision."}
        </p>

        <div className="mt-5 space-y-4">
          <label className="block text-sm font-medium text-[#CBD5E1]">
            Reviewer <span className="font-normal text-[#64748B]">optional</span>
            <input
              value={resolvedBy}
              onChange={(event) => setResolvedBy(event.target.value)}
              className="mt-2 w-full rounded-xl border border-[#26334D] bg-[#0A1020] px-4 py-3 text-sm text-white outline-none transition placeholder:text-[#64748B] focus:border-[#7C5CFC]"
              placeholder="Who reviewed this?"
              disabled={busy}
            />
          </label>
          <label className="block text-sm font-medium text-[#CBD5E1]">
            {approving ? "Approval note" : "Rejection reason"} <span className="font-normal text-[#64748B]">optional</span>
            <textarea
              value={reason}
              onChange={(event) => setReason(event.target.value)}
              className="mt-2 min-h-24 w-full resize-y rounded-xl border border-[#26334D] bg-[#0A1020] px-4 py-3 text-sm leading-6 text-white outline-none transition placeholder:text-[#64748B] focus:border-[#7C5CFC]"
              placeholder={approving ? "Why is this safe to approve?" : "Why should this remain blocked?"}
              disabled={busy}
            />
          </label>
        </div>

        {error && <p className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{error}</p>}

        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <Button variant="secondary" onClick={handleClose} disabled={busy}>Cancel</Button>
          <Button variant={approving ? "primary" : "danger"} onClick={handleConfirm} disabled={busy}>
            {busy ? "Submitting..." : approving ? "Approve" : "Reject"}
          </Button>
        </div>
      </div>
    </div>
  );
}


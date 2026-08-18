"use client";

import { useId, useState } from "react";

import Button from "@/components/ui/Button";
import { createMemory } from "@/lib/api/memory";
import type { JsonValue, MemoryResponse, MemoryType } from "@/types/api";

import { MEMORY_TYPES, label } from "./memory-utils";

type CreateMemoryDialogProps = {
  open: boolean;
  onClose: () => void;
  onCreated: (memory: MemoryResponse) => void;
};

export default function CreateMemoryDialog({ open, onClose, onCreated }: CreateMemoryDialogProps) {
  const titleId = useId();
  const [content, setContent] = useState("");
  const [memoryType, setMemoryType] = useState<MemoryType>("fact");
  const [importance, setImportance] = useState(0.5);
  const [metadataText, setMetadataText] = useState("");
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  function reset() {
    setContent("");
    setMemoryType("fact");
    setImportance(0.5);
    setMetadataText("");
    setAdvancedOpen(false);
    setError(null);
  }

  function close() {
    reset();
    onClose();
  }

  async function handleSubmit() {
    const trimmed = content.trim();
    if (!trimmed) {
      setError("Memory content is required.");
      return;
    }

    let metadata: Record<string, JsonValue> = {};
    if (metadataText.trim()) {
      try {
        const parsed = JSON.parse(metadataText) as JsonValue;
        if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
          setError("Metadata must be a JSON object.");
          return;
        }
        metadata = parsed as Record<string, JsonValue>;
      } catch {
        setError("Metadata must be valid JSON.");
        return;
      }
    }

    setSubmitting(true);
    setError(null);

    try {
      const memory = await createMemory({ content: trimmed, memory_type: memoryType, importance, metadata });
      onCreated(memory);
      close();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to add memory.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4" role="dialog" aria-modal="true" aria-labelledby={titleId}>
      <div className="w-full max-w-2xl rounded-[22px] border border-[#26334D] bg-[#0D1321] p-6 shadow-2xl shadow-black/50">
        <h2 id={titleId} className="text-xl font-semibold text-white">Add Memory</h2>
        <p className="mt-2 text-sm text-[#94A3B8]">Store useful context for AURA to retain across work.</p>

        <div className="mt-5 space-y-4">
          <label className="block text-sm font-medium text-[#CBD5E1]">
            Content
            <textarea value={content} onChange={(event) => setContent(event.target.value)} className="mt-2 min-h-32 w-full resize-y rounded-xl border border-[#26334D] bg-[#0A1020] px-4 py-3 text-sm leading-6 text-white outline-none focus:border-[#7C5CFC]" placeholder="What should AURA remember?" disabled={submitting} />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm font-medium text-[#CBD5E1]">
              Memory type
              <select value={memoryType} onChange={(event) => setMemoryType(event.target.value as MemoryType)} className="mt-2 h-11 w-full rounded-xl border border-[#26334D] bg-[#0A1020] px-4 text-sm text-white outline-none focus:border-[#7C5CFC]" disabled={submitting}>
                {MEMORY_TYPES.map((type) => <option key={type} value={type}>{label(type)}</option>)}
              </select>
            </label>
            <label className="block text-sm font-medium text-[#CBD5E1]">
              Importance: {importance.toFixed(2)}
              <input type="range" min="0" max="1" step="0.01" value={importance} onChange={(event) => setImportance(Number(event.target.value))} className="mt-4 w-full accent-[#7C5CFC]" disabled={submitting} />
            </label>
          </div>

          <details open={advancedOpen} onToggle={(event) => setAdvancedOpen(event.currentTarget.open)} className="rounded-xl border border-[#26334D] bg-[#0A1020] p-4">
            <summary className="cursor-pointer text-sm font-medium text-[#CBD5E1]">Advanced metadata</summary>
            <label className="mt-4 block text-sm text-[#94A3B8]">
              Optional JSON object
              <textarea value={metadataText} onChange={(event) => setMetadataText(event.target.value)} className="mt-2 min-h-24 w-full resize-y rounded-xl border border-[#26334D] bg-[#050A14] px-4 py-3 font-mono text-xs leading-5 text-white outline-none focus:border-[#7C5CFC]" placeholder={'{"source":"manual"}'} disabled={submitting} />
            </label>
          </details>
        </div>

        {error && <p className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{error}</p>}

        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <Button variant="secondary" onClick={close} disabled={submitting}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={submitting}>{submitting ? "Adding..." : "Add Memory"}</Button>
        </div>
      </div>
    </div>
  );
}


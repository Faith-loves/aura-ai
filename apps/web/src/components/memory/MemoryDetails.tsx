"use client";

import Link from "next/link";
import { ArrowLeft, Brain, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { formatJson, hasMetadata, label } from "@/components/memory/memory-utils";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { deleteMemory, getMemory } from "@/lib/api/memory";
import type { MemoryResponse } from "@/types/api";

export default function MemoryDetails({ memoryId }: { memoryId: string }) {
  const router = useRouter();
  const [memory, setMemory] = useState<MemoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const loadMemory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setMemory(await getMemory(memoryId));
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to load memory.");
    } finally {
      setLoading(false);
    }
  }, [memoryId]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadMemory();
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, [loadMemory]);

  async function handleDelete() {
    if (!memory) return;
    if (!window.confirm("Delete memory? This permanently removes this stored memory from AURA.")) return;
    setDeleting(true);
    setActionError(null);
    try {
      await deleteMemory(memory.id);
      router.push("/memory");
    } catch (nextError) {
      setActionError(nextError instanceof Error ? nextError.message : "Unable to delete memory.");
      setDeleting(false);
    }
  }

  if (loading) {
    return <Card className="mx-auto max-w-5xl p-6"><div className="h-6 w-64 animate-pulse rounded bg-[#1D2942]" /><div className="mt-6 h-80 animate-pulse rounded-2xl bg-[#1D2942]/50" /></Card>;
  }

  if (error || !memory) {
    return <Card className="mx-auto max-w-5xl p-6"><h1 className="text-xl font-semibold text-white">Memory unavailable</h1><p className="mt-2 text-sm text-[#94A3B8]">{error ?? "Memory not found."}</p><Button className="mt-5" onClick={loadMemory}>Retry</Button></Card>;
  }

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <Link href="/memory" className="inline-flex items-center gap-2 text-sm text-[#94A3B8] transition hover:text-white"><ArrowLeft size={16} />Back to memory</Link>

      <section className="rounded-[20px] border border-[#1D2942] bg-[#0D1321]/78 p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2"><Badge variant="purple">{label(memory.memory_type)}</Badge><Badge variant="info">Importance {memory.importance.toFixed(2)}</Badge>{hasMetadata(memory.metadata) && <Badge variant="default">Metadata</Badge>}</div>
            <h1 className="mt-4 flex items-center gap-3 text-3xl font-semibold tracking-tight text-white"><Brain size={28} />Memory Detail</h1>
            <p className="mt-2 break-all text-xs text-[#64748B]">ID {memory.id}</p>
          </div>
          <Button variant="danger" onClick={handleDelete} disabled={deleting}><Trash2 size={16} />{deleting ? "Deleting..." : "Delete"}</Button>
        </div>
        {actionError && <p className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{actionError}</p>}
      </section>

      <Card className="p-5 sm:p-6">
        <h2 className="text-lg font-semibold text-white">Content</h2>
        <p className="mt-4 whitespace-pre-wrap break-words text-sm leading-7 text-[#CBD5E1]">{memory.content}</p>
      </Card>

      <section className="grid gap-4 md:grid-cols-3">
        <Info label="Memory Type" value={label(memory.memory_type)} />
        <Info label="Importance" value={memory.importance.toFixed(2)} />
        <Info label="Access Count" value={String(memory.access_count)} />
      </section>

      <details className="rounded-2xl border border-[#1D2942] bg-[#0D1321]/78 p-5">
        <summary className="cursor-pointer text-sm font-medium text-[#CBD5E1]">Technical details</summary>
        <pre className="mt-4 max-h-80 overflow-auto whitespace-pre-wrap break-words rounded-xl bg-[#0A1020] p-4 text-xs leading-5 text-[#94A3B8]">{formatJson(memory.metadata)}</pre>
      </details>
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return <div className="rounded-2xl border border-[#1D2942] bg-[#0D1321]/78 p-4"><p className="text-xs uppercase tracking-[0.14em] text-[#64748B]">{label}</p><p className="mt-2 text-sm font-medium text-white">{value}</p></div>;
}

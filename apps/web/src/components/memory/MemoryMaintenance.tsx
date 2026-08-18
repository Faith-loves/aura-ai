"use client";

import { Download, FileUp, Save, ShieldAlert, Trash2 } from "lucide-react";
import { useState } from "react";

import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { backupMemory, cleanupContaminatedMemory, cleanupMemory, clearAllMemory, exportMemory, importMemory, restoreMemory } from "@/lib/api/memory";
import type { ImportMemoryRequest, MemoryActionResponse } from "@/types/api";

type MemoryMaintenanceProps = {
  onChanged: () => Promise<void> | void;
};

function downloadJson(filename: string, payload: unknown) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function summarizeAction(result: MemoryActionResponse) {
  if (typeof result.deleted === "number") return `${result.deleted} memories deleted.`;
  if (typeof result.imported === "number") return `${result.imported} memories imported.`;
  if (result.path) return `Backup created at backend path: ${result.path}`;
  if (typeof result.current_count === "number") return `Restore complete. Current memory count: ${result.current_count}.`;
  return "Memory action completed.";
}

export default function MemoryMaintenance({ onChanged }: MemoryMaintenanceProps) {
  const [minImportance, setMinImportance] = useState(0.3);
  const [maxAccessCount, setMaxAccessCount] = useState(0);
  const [olderThanDays, setOlderThanDays] = useState(30);
  const [restorePath, setRestorePath] = useState("");
  const [clearExisting, setClearExisting] = useState(true);
  const [importText, setImportText] = useState("");
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function runAction(name: string, action: () => Promise<MemoryActionResponse>, options: { destructive?: boolean; confirm?: string } = {}) {
    if (options.confirm && !window.confirm(options.confirm)) return;
    if (options.destructive && !window.confirm("Please confirm again. This action removes memory data from AURA.")) return;

    setBusyAction(name);
    setNotice(null);
    setError(null);

    try {
      const result = await action();
      setNotice(summarizeAction(result));
      await onChanged();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Memory maintenance action failed.");
    } finally {
      setBusyAction(null);
    }
  }

  async function handleExport() {
    setBusyAction("export");
    setNotice(null);
    setError(null);

    try {
      const data = await exportMemory();
      downloadJson("aura-memory-export.json", data);
      setNotice(`Export prepared with ${data.count} memories.`);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Unable to export memory.");
    } finally {
      setBusyAction(null);
    }
  }

  async function handleImport() {
    let parsed: unknown;
    try {
      parsed = JSON.parse(importText);
    } catch {
      setError("Import data must be valid JSON.");
      return;
    }

    if (!parsed || typeof parsed !== "object" || !Array.isArray((parsed as { memories?: unknown }).memories)) {
      setError("Import JSON must include a memories array.");
      return;
    }

    await runAction("import", () => importMemory(parsed as ImportMemoryRequest), { confirm: "Import these memories into AURA? Existing memories with matching IDs may be overwritten." });
  }

  return (
    <Card className="p-5 sm:p-6">
      <div className="flex items-start gap-3">
        <ShieldAlert size={22} className="mt-1 text-[#F59E0B]" />
        <div>
          <h2 className="text-lg font-semibold text-white">Memory Maintenance</h2>
          <p className="mt-1 text-sm leading-6 text-[#94A3B8]">Administrative actions affect stored AURA memory. Export downloads JSON in your browser; backup/restore use backend filesystem paths.</p>
        </div>
      </div>

      {notice && <p className="mt-4 rounded-xl border border-[#22C55E]/30 bg-[#22C55E]/10 px-3 py-2 text-sm text-[#86EFAC]">{notice}</p>}
      {error && <p className="mt-4 rounded-xl border border-[#EF4444]/30 bg-[#EF4444]/10 px-3 py-2 text-sm text-[#FCA5A5]">{error}</p>}

      <div className="mt-5 flex flex-wrap gap-2">
        <Button variant="secondary" onClick={handleExport} disabled={busyAction !== null}><Download size={15} />Export Memory</Button>
        <Button variant="secondary" onClick={() => runAction("backup", backupMemory)} disabled={busyAction !== null}><Save size={15} />Create Backup</Button>
        <Button variant="danger" onClick={() => runAction("contaminated", cleanupContaminatedMemory, { confirm: "Clean contaminated memory? This removes memories identified by AURA as contaminated or invalid." })} disabled={busyAction !== null}>Cleanup Contaminated</Button>
        <Button variant="danger" onClick={() => runAction("clear", clearAllMemory, { destructive: true, confirm: "Clear all memory? This removes all memories stored by AURA." })} disabled={busyAction !== null}><Trash2 size={15} />Clear All Memory</Button>
      </div>

      <details className="mt-5 rounded-xl border border-[#26334D] bg-[#0A1020] p-4">
        <summary className="cursor-pointer text-sm font-medium text-[#CBD5E1]">Cleanup rules</summary>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <label className="text-sm text-[#CBD5E1]">Min importance
            <input type="number" min="0" max="1" step="0.01" value={minImportance} onChange={(event) => setMinImportance(Number(event.target.value))} className="mt-2 h-10 w-full rounded-xl border border-[#26334D] bg-[#050A14] px-3 text-white outline-none focus:border-[#7C5CFC]" />
          </label>
          <label className="text-sm text-[#CBD5E1]">Max access count
            <input type="number" min="0" step="1" value={maxAccessCount} onChange={(event) => setMaxAccessCount(Number(event.target.value))} className="mt-2 h-10 w-full rounded-xl border border-[#26334D] bg-[#050A14] px-3 text-white outline-none focus:border-[#7C5CFC]" />
          </label>
          <label className="text-sm text-[#CBD5E1]">Older than days
            <input type="number" min="0" step="1" value={olderThanDays} onChange={(event) => setOlderThanDays(Number(event.target.value))} className="mt-2 h-10 w-full rounded-xl border border-[#26334D] bg-[#050A14] px-3 text-white outline-none focus:border-[#7C5CFC]" />
          </label>
        </div>
        <Button className="mt-4" variant="danger" onClick={() => runAction("cleanup", () => cleanupMemory({ min_importance: minImportance, max_access_count: maxAccessCount, older_than_days: olderThanDays }), { confirm: "Run memory cleanup using these deletion rules?" })} disabled={busyAction !== null}>Cleanup Memory</Button>
      </details>

      <details className="mt-4 rounded-xl border border-[#26334D] bg-[#0A1020] p-4">
        <summary className="cursor-pointer text-sm font-medium text-[#CBD5E1]">Import / restore</summary>
        <div className="mt-4 grid gap-5 xl:grid-cols-2">
          <label className="text-sm text-[#CBD5E1]">Import JSON
            <textarea value={importText} onChange={(event) => setImportText(event.target.value)} className="mt-2 min-h-32 w-full resize-y rounded-xl border border-[#26334D] bg-[#050A14] px-3 py-3 font-mono text-xs leading-5 text-white outline-none focus:border-[#7C5CFC]" placeholder='{"version":1,"memories":[]}' />
            <Button className="mt-3" variant="secondary" onClick={handleImport} disabled={busyAction !== null || !importText.trim()}><FileUp size={15} />Import JSON</Button>
          </label>
          <div>
            <label className="text-sm text-[#CBD5E1]">Backend backup file path
              <input value={restorePath} onChange={(event) => setRestorePath(event.target.value)} className="mt-2 h-10 w-full rounded-xl border border-[#26334D] bg-[#050A14] px-3 text-white outline-none focus:border-[#7C5CFC]" placeholder="backups/aura_memory_...json" />
            </label>
            <label className="mt-3 flex items-center gap-2 text-sm text-[#CBD5E1]"><input type="checkbox" checked={clearExisting} onChange={(event) => setClearExisting(event.target.checked)} className="accent-[#7C5CFC]" />Clear existing memory before restore</label>
            <Button className="mt-3" variant="danger" onClick={() => runAction("restore", () => restoreMemory({ file_path: restorePath, clear_existing: clearExisting }), { destructive: clearExisting, confirm: "Restore memory from this backend path?" })} disabled={busyAction !== null || !restorePath.trim()}>Restore From Backend Path</Button>
          </div>
        </div>
      </details>
    </Card>
  );
}


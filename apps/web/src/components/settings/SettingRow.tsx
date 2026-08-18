import type { ReactNode } from "react";

import Badge from "@/components/ui/Badge";

export default function SettingRow({ label, description, value, readOnly = false }: { label: string; description?: string; value: ReactNode; readOnly?: boolean }) {
  return (
    <div className="flex flex-col gap-3 border-t border-[#162036] py-4 first:border-t-0 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-sm font-medium text-[#F8FAFC]">{label}</p>
          {readOnly && <Badge variant="default">Read only</Badge>}
        </div>
        {description && <p className="mt-1 text-xs leading-5 text-[#64748B]">{description}</p>}
      </div>
      <div className="min-w-0 text-sm font-medium text-[#CBD5E1] sm:text-right">{value}</div>
    </div>
  );
}

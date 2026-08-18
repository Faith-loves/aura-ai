import type {
  DashboardSubsystemStatus,
} from "@/types/dashboard";

const statusClasses: Record<DashboardSubsystemStatus, string> = {
  healthy: "bg-[#22C55E] shadow-[0_0_10px_rgba(34,197,94,0.42)]",
  degraded: "bg-[#F59E0B] shadow-[0_0_10px_rgba(245,158,11,0.35)]",
  unavailable: "bg-[#EF4444] shadow-[0_0_10px_rgba(239,68,68,0.35)]",
};

type StatusIndicatorProps = {
  status: DashboardSubsystemStatus;
  label: string;
  className?: string;
};

export default function StatusIndicator({
  status,
  label,
  className = "",
}: StatusIndicatorProps) {
  return (
    <span className={`inline-flex items-center gap-2 ${className}`}>
      <span className={`h-2 w-2 rounded-full ${statusClasses[status]}`} />
      <span>{label}</span>
    </span>
  );
}

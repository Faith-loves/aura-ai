import Badge from "@/components/ui/Badge";
import type { RiskLevel } from "@/types/api";

type RiskBadgeProps = {
  risk: RiskLevel | string | null;
};

const riskText: Record<RiskLevel, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  critical: "Critical",
};

const riskTitle: Record<RiskLevel, string> = {
  low: "Routine action",
  medium: "Sensitive operation",
  high: "Manual approval may be required",
  critical: "Blocked by the default policy",
};

export default function RiskBadge({ risk }: RiskBadgeProps) {
  if (!risk) {
    return <Badge variant="default">No risk</Badge>;
  }

  const normalized = risk.toLowerCase() as RiskLevel;
  const variant = normalized === "critical" ? "danger" : normalized === "high" ? "warning" : normalized === "medium" ? "info" : "success";

  return (
    <span title={riskTitle[normalized] ?? "Safety risk level"}>
      <Badge variant={variant}>{riskText[normalized] ?? risk}</Badge>
    </span>
  );
}

import Badge from "@/components/ui/Badge";
import type { ApprovalStatus } from "@/types/api";

type ApprovalStatusBadgeProps = {
  status: ApprovalStatus;
};

function label(status: ApprovalStatus) {
  return status.split("_").map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`).join(" ");
}

export default function ApprovalStatusBadge({ status }: ApprovalStatusBadgeProps) {
  const variant = status === "approved" ? "success" : status === "rejected" ? "danger" : status === "pending" ? "warning" : "default";
  return <Badge variant={variant}>{label(status)}</Badge>;
}

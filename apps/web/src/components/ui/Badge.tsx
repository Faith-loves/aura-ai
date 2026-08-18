import type {
  ReactNode,
} from "react";

const variantClasses = {
  default: "border-[#26334D] bg-[#111A2E] text-[#94A3B8]",
  success: "border-[#22C55E]/30 bg-[#22C55E]/10 text-[#86EFAC]",
  warning: "border-[#F59E0B]/30 bg-[#F59E0B]/10 text-[#FCD34D]",
  danger: "border-[#EF4444]/30 bg-[#EF4444]/10 text-[#FCA5A5]",
  info: "border-[#38BDF8]/30 bg-[#38BDF8]/10 text-[#7DD3FC]",
  purple: "border-[#7C5CFC]/35 bg-[#7C5CFC]/12 text-[#C4B5FD]",
};

type BadgeVariant = keyof typeof variantClasses;

type BadgeProps = {
  children: ReactNode;
  variant?: BadgeVariant;
};

export default function Badge({
  children,
  variant = "default",
}: BadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium ${variantClasses[variant]}`}>
      {children}
    </span>
  );
}

type StatusTone =
  | "neutral"
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "purple";


type StatusBadgeProps = {
  label: string;

  tone?: StatusTone;

  dot?: boolean;

  pulse?: boolean;
};


const tones: Record<
  StatusTone,
  string
> = {
  neutral:
    "border-[#26334D] bg-[#111A2E] text-[#94A3B8]",

  success:
    "border-[#22C55E]/20 bg-[#22C55E]/10 text-[#4ADE80]",

  warning:
    "border-[#F59E0B]/20 bg-[#F59E0B]/10 text-[#FBBF24]",

  danger:
    "border-[#EF4444]/20 bg-[#EF4444]/10 text-[#F87171]",

  info:
    "border-[#38BDF8]/20 bg-[#38BDF8]/10 text-[#7DD3FC]",

  purple:
    "border-[#7C5CFC]/20 bg-[#7C5CFC]/10 text-[#A78BFA]",
};


const dotTones: Record<
  StatusTone,
  string
> = {
  neutral:
    "bg-[#64748B]",

  success:
    "bg-[#22C55E]",

  warning:
    "bg-[#F59E0B]",

  danger:
    "bg-[#EF4444]",

  info:
    "bg-[#38BDF8]",

  purple:
    "bg-[#7C5CFC]",
};


export default function StatusBadge({
  label,
  tone = "neutral",
  dot = true,
  pulse = false,
}: StatusBadgeProps) {
  return (
    <span
      className={`
        inline-flex
        items-center
        gap-1.5
        rounded-full
        border
        px-2.5
        py-1
        text-[11px]
        font-medium
        ${tones[tone]}
      `}
    >
      {dot && (
        <span
          className={`
            h-1.5
            w-1.5
            rounded-full
            ${dotTones[tone]}
            ${
              pulse
                ? "animate-pulse"
                : ""
            }
          `}
        />
      )}

      {label}
    </span>
  );
}
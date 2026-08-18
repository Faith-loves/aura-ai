import type {
  ButtonHTMLAttributes,
} from "react";

const variantClasses = {
  primary: "bg-[#7C5CFC] text-white shadow-lg shadow-[#7C5CFC]/20 hover:bg-[#9B87FF]",
  secondary: "border border-[#26334D] bg-[#111A2E] text-[#CBD5E1] hover:border-[#3A4866] hover:bg-[#162036]",
  danger: "border border-[#EF4444]/30 bg-[#EF4444]/10 text-[#FCA5A5] hover:bg-[#EF4444]/15",
  ghost: "bg-transparent text-[#94A3B8] hover:bg-white/[0.05] hover:text-white",
};

type ButtonVariant = keyof typeof variantClasses;

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
};

export default function Button({
  variant = "primary",
  className = "",
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`inline-flex h-10 items-center justify-center gap-2 rounded-xl px-4 text-sm font-medium transition duration-150 disabled:pointer-events-none disabled:opacity-45 ${variantClasses[variant]} ${className}`}
      {...props}
    />
  );
}

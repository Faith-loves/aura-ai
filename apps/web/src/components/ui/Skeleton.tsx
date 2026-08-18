import type {
  HTMLAttributes,
} from "react";


type SkeletonProps =
  HTMLAttributes<HTMLDivElement>;


export default function Skeleton({
  className = "",
  ...props
}: SkeletonProps) {
  return (
    <div
      {...props}
      className={`
        animate-pulse
        rounded-lg
        bg-white/[0.06]
        ${className}
      `}
    />
  );
}
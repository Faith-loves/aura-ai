import type {
  HTMLAttributes,
  ReactNode,
} from "react";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
  className?: string;
};

export default function Card({
  children,
  className = "",
  ...props
}: CardProps) {
  return (
    <div className={`aura-card ${className}`} {...props}>
      {children}
    </div>
  );
}

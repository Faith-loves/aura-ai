import type {
  ReactNode,
} from "react";


type PageContainerProps = {
  children: ReactNode;

  className?: string;

  size?:
    | "default"
    | "narrow"
    | "wide";
};


const sizes = {
  default:
    "max-w-[1400px]",

  narrow:
    "max-w-[1050px]",

  wide:
    "max-w-[1600px]",
};


export default function PageContainer({
  children,
  className = "",
  size = "default",
}: PageContainerProps) {
  return (
    <div
      className={`
        mx-auto
        w-full
        ${sizes[size]}
        ${className}
      `}
    >
      {children}
    </div>
  );
}
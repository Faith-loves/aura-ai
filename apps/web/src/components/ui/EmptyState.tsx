import type {
  ReactNode,
} from "react";

import {
  Inbox,
} from "lucide-react";


type EmptyStateProps = {
  title: string;
  description: string;

  icon?: ReactNode;

  action?: ReactNode;

  className?: string;
};


export default function EmptyState({
  title,
  description,
  icon,
  action,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`
        flex
        min-h-[320px]
        w-full
        flex-col
        items-center
        justify-center
        rounded-2xl
        border
        border-dashed
        border-[#26334D]
        bg-[#0D1321]/60
        px-6
        py-12
        text-center
        ${className}
      `}
    >
      <div
        className="
          flex
          h-14
          w-14
          items-center
          justify-center
          rounded-2xl
          border
          border-[#7C5CFC]/20
          bg-[#7C5CFC]/10
          text-[#9B87FF]
        "
      >
        {icon ?? (
          <Inbox
            size={24}
            strokeWidth={1.8}
          />
        )}
      </div>

      <h2
        className="
          mb-0
          mt-5
          text-lg
          font-semibold
          tracking-[-0.02em]
          text-white
        "
      >
        {title}
      </h2>

      <p
        className="
          mb-0
          mt-2
          max-w-md
          text-sm
          leading-6
          text-[#94A3B8]
        "
      >
        {description}
      </p>

      {action && (
        <div
          className="
            mt-6
            flex
            items-center
            justify-center
          "
        >
          {action}
        </div>
      )}
    </div>
  );
}
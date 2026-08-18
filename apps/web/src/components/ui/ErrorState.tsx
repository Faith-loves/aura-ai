import {
  AlertTriangle,
  RefreshCw,
} from "lucide-react";

import Button from "./Button";


type ErrorStateProps = {
  title?: string;
  description?: string;
  error?: string | null;
  onRetry?: () => void;
  retrying?: boolean;
  compact?: boolean;
};


export default function ErrorState({
  title = "Something went wrong",
  description = (
    "AURA could not load this information."
  ),
  error,
  onRetry,
  retrying = false,
  compact = false,
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className={`
        flex
        w-full
        flex-col
        items-center
        justify-center
        rounded-2xl
        border
        border-[#EF4444]/20
        bg-[#EF4444]/[0.04]
        px-6
        text-center
        ${
          compact
            ? "min-h-[200px] py-8"
            : "min-h-[320px] py-12"
        }
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
          border-[#EF4444]/20
          bg-[#EF4444]/10
          text-[#F87171]
        "
      >
        <AlertTriangle
          size={24}
          strokeWidth={1.8}
        />
      </div>

      <h2
        className="
          mb-0
          mt-5
          text-lg
          font-semibold
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

      {error && (
        <p
          className="
            mb-0
            mt-3
            max-w-lg
            rounded-lg
            border
            border-[#EF4444]/10
            bg-[#EF4444]/5
            px-3
            py-2
            text-xs
            text-[#FCA5A5]
          "
        >
          {error}
        </p>
      )}

      {onRetry && (
        <Button
          type="button"
          variant="secondary"
          className="mt-6"
          disabled={retrying}
          onClick={onRetry}
        >
          <RefreshCw
            size={15}
            className={
              retrying
                ? "animate-spin"
                : ""
            }
          />

          {retrying
            ? "Retrying..."
            : "Retry"}
        </Button>
      )}
    </div>
  );
}
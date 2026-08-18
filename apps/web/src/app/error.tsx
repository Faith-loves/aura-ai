"use client";

import {
  useEffect,
} from "react";

import ErrorState from "@/components/ui/ErrorState";


export default function Error({
  error,
  reset,
}: {
  error: Error & {
    digest?: string;
  };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(
      "AURA interface error:",
      error
    );
  }, [error]);

  return (
    <div
      className="
        mx-auto
        flex
        min-h-[calc(100vh-130px)]
        w-full
        max-w-[1100px]
        items-center
        justify-center
      "
    >
      <ErrorState
        title="AURA encountered an interface error"
        description="
          The current screen could not be displayed correctly.
          Your AURA runtime has not been reset.
        "
        error={
          error.message
          || "Unknown interface error."
        }
        onRetry={reset}
      />
    </div>
  );
}
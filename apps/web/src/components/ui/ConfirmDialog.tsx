"use client";

import {
  AlertTriangle,
  X,
} from "lucide-react";

import Button from "./Button";


type ConfirmDialogProps = {
  open: boolean;

  title: string;

  description: string;

  confirmLabel?: string;

  cancelLabel?: string;

  variant?:
    | "danger"
    | "primary";

  loading?: boolean;

  onConfirm: () => void;

  onCancel: () => void;
};


export default function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  variant = "danger",
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!open) {
    return null;
  }

  return (
    <div
      className="
        fixed
        inset-0
        z-[100]
        flex
        items-center
        justify-center
        bg-black/60
        px-4
        backdrop-blur-sm
      "
      role="presentation"
      onMouseDown={(event) => {
        if (
          event.target
          === event.currentTarget
        ) {
          onCancel();
        }
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        aria-describedby="confirm-description"
        className="
          w-full
          max-w-md
          rounded-2xl
          border
          border-[#26334D]
          bg-[#0D1321]
          p-5
          shadow-2xl
          shadow-black/40
        "
      >
        <div
          className="
            flex
            items-start
            justify-between
            gap-4
          "
        >
          <div
            className="
              flex
              h-11
              w-11
              shrink-0
              items-center
              justify-center
              rounded-xl
              border
              border-[#EF4444]/20
              bg-[#EF4444]/10
              text-[#F87171]
            "
          >
            <AlertTriangle size={20} />
          </div>

          <button
            type="button"
            aria-label="Close dialog"
            className="
              flex
              h-8
              w-8
              items-center
              justify-center
              rounded-lg
              text-[#64748B]
              transition
              hover:bg-white/[0.05]
              hover:text-white
            "
            onClick={onCancel}
          >
            <X size={17} />
          </button>
        </div>

        <h2
          id="confirm-title"
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
          id="confirm-description"
          className="
            mb-0
            mt-2
            text-sm
            leading-6
            text-[#94A3B8]
          "
        >
          {description}
        </p>

        <div
          className="
            mt-6
            flex
            justify-end
            gap-3
          "
        >
          <Button
            type="button"
            variant="ghost"
            disabled={loading}
            onClick={onCancel}
          >
            {cancelLabel}
          </Button>

          <Button
            type="button"
            variant={
              variant === "danger"
                ? "danger"
                : "primary"
            }
            disabled={loading}
            onClick={onConfirm}
          >
            {loading
              ? "Working..."
              : confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
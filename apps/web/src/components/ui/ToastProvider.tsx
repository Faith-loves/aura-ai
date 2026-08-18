"use client";

import {
  CheckCircle2,
  CircleAlert,
  Info,
  X,
} from "lucide-react";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

import type {
  ReactNode,
} from "react";


type ToastType =
  | "success"
  | "error"
  | "info";


type Toast = {
  id: string;
  title: string;
  description?: string;
  type: ToastType;
};


type ToastInput = {
  title: string;
  description?: string;
  type?: ToastType;
};


type ToastContextValue = {
  showToast: (
    toast: ToastInput
  ) => void;
};


const ToastContext =
  createContext<
    ToastContextValue | undefined
  >(undefined);


export function ToastProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [
    toasts,
    setToasts,
  ] = useState<Toast[]>([]);

  const removeToast =
    useCallback(
      (id: string) => {
        setToasts((current) =>
          current.filter(
            (toast) =>
              toast.id !== id
          )
        );
      },
      []
    );

  const showToast =
    useCallback(
      ({
        title,
        description,
        type = "info",
      }: ToastInput) => {
        const id =
          crypto.randomUUID();

        const toast: Toast = {
          id,
          title,
          description,
          type,
        };

        setToasts((current) => [
          ...current,
          toast,
        ]);

        window.setTimeout(() => {
          removeToast(id);
        }, 4500);
      },
      [removeToast]
    );

  const value = useMemo(
    () => ({
      showToast,
    }),
    [showToast]
  );

  return (
    <ToastContext.Provider
      value={value}
    >
      {children}

      <div
        aria-live="polite"
        aria-atomic="false"
        className="
          fixed
          bottom-5
          right-5
          z-[120]
          flex
          w-[min(380px,calc(100vw-40px))]
          flex-col
          gap-3
        "
      >
        {toasts.map((toast) => (
          <ToastItem
            key={toast.id}
            toast={toast}
            onClose={() =>
              removeToast(
                toast.id
              )
            }
          />
        ))}
      </div>
    </ToastContext.Provider>
  );
}


export function useToast() {
  const context =
    useContext(ToastContext);

  if (!context) {
    throw new Error(
      "useToast must be used inside ToastProvider."
    );
  }

  return context;
}


function ToastItem({
  toast,
  onClose,
}: {
  toast: Toast;
  onClose: () => void;
}) {
  const appearance = {
    success: {
      icon: CheckCircle2,
      border:
        "border-[#22C55E]/20",
      background:
        "bg-[#0D1714]",
      iconColor:
        "text-[#4ADE80]",
    },

    error: {
      icon: CircleAlert,
      border:
        "border-[#EF4444]/20",
      background:
        "bg-[#180F14]",
      iconColor:
        "text-[#F87171]",
    },

    info: {
      icon: Info,
      border:
        "border-[#38BDF8]/20",
      background:
        "bg-[#0C151D]",
      iconColor:
        "text-[#7DD3FC]",
    },
  }[toast.type];

  const Icon = appearance.icon;

  return (
    <div
      className={`
        flex
        items-start
        gap-3
        rounded-2xl
        border
        p-4
        shadow-2xl
        shadow-black/30
        backdrop-blur-xl
        ${appearance.border}
        ${appearance.background}
      `}
    >
      <Icon
        size={19}
        className={`
          mt-0.5
          shrink-0
          ${appearance.iconColor}
        `}
      />

      <div className="min-w-0 flex-1">
        <p
          className="
            m-0
            text-sm
            font-medium
            text-white
          "
        >
          {toast.title}
        </p>

        {toast.description && (
          <p
            className="
              mb-0
              mt-1
              text-xs
              leading-5
              text-[#94A3B8]
            "
          >
            {toast.description}
          </p>
        )}
      </div>

      <button
        type="button"
        aria-label="Dismiss notification"
        onClick={onClose}
        className="
          flex
          h-7
          w-7
          shrink-0
          items-center
          justify-center
          rounded-lg
          text-[#64748B]
          transition
          hover:bg-white/[0.05]
          hover:text-white
        "
      >
        <X size={15} />
      </button>
    </div>
  );
}
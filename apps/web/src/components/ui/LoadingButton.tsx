import {
  LoaderCircle,
} from "lucide-react";

import type {
  ComponentProps,
} from "react";

import Button from "./Button";


type LoadingButtonProps =
  ComponentProps<typeof Button> & {
    loading?: boolean;
    loadingText?: string;
  };


export default function LoadingButton({
  loading = false,
  loadingText = "Working...",
  disabled,
  children,
  ...props
}: LoadingButtonProps) {
  return (
    <Button
      {...props}
      disabled={
        loading
        || disabled
      }
    >
      {loading && (
        <LoaderCircle
          size={16}
          className="animate-spin"
        />
      )}

      {loading
        ? loadingText
        : children}
    </Button>
  );
}
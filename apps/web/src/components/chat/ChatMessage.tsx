import {
  AlertTriangle,
  RotateCcw,
  Sparkles,
  User,
} from "lucide-react";

import Button from "@/components/ui/Button";
import type {
  ChatMessage as ChatMessageType,
} from "@/types/chat";

function formatTimestamp(isoTimestamp: string) {
  const date = new Date(isoTimestamp);

  if (Number.isNaN(date.getTime())) {
    return "Now";
  }

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-3 text-sm text-[#94A3B8]" aria-live="polite">
      <Sparkles size={16} className="text-[#9B87FF]" />
      <span>AURA is working</span>
      <span className="flex gap-1" aria-hidden="true">
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#7C5CFC] [animation-delay:-0.2s]" />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#9B87FF] [animation-delay:-0.1s]" />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#2DD4BF]" />
      </span>
    </div>
  );
}

type ChatMessageProps = {
  message: ChatMessageType;
  onRetry?: (prompt: string) => void;
  requestActive?: boolean;
};

export default function ChatMessage({
  message,
  onRetry,
  requestActive = false,
}: ChatMessageProps) {
  const isUser = message.role === "user";
  const isError = message.status === "error";
  const retryPrompt = message.metadata?.retryPrompt;

  return (
    <article className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#7C5CFC] text-white shadow-lg shadow-[#7C5CFC]/20">
          {isError ? <AlertTriangle size={17} /> : <Sparkles size={17} />}
        </div>
      )}

      <div className={`max-w-[min(760px,100%)] ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        <div
          className={`rounded-2xl border px-4 py-3 ${
            isUser
              ? "border-[#7C5CFC]/25 bg-[#7C5CFC]/16 text-[#F8FAFC]"
              : isError
                ? "border-[#EF4444]/30 bg-[#EF4444]/10 text-[#FEE2E2]"
                : "border-[#1D2942] bg-[#111A2E]/86 text-[#E2E8F0]"
          }`}
        >
          {message.status === "thinking" ? (
            <ThinkingIndicator />
          ) : (
            <p className="whitespace-pre-wrap text-sm leading-7">{message.content}</p>
          )}

          {message.metadata?.provider && message.status === "completed" && (
            <div className="mt-3 border-t border-[#26334D] pt-2 text-[11px] text-[#64748B]">
              Provider: {message.metadata.provider}
              {message.metadata.model ? ` · Model: ${message.metadata.model}` : ""}
              {message.metadata.usedFallback ? " · Fallback used" : ""}
            </div>
          )}

          {isError && retryPrompt && onRetry && (
            <div className="mt-3">
              <Button
                variant="secondary"
                className="h-8 px-3 text-xs"
                onClick={() => onRetry(retryPrompt)}
                disabled={requestActive}
              >
                <RotateCcw size={14} />
                Retry
              </Button>
            </div>
          )}
        </div>

        <div className="mt-1 flex items-center gap-2 px-1 text-[11px] text-[#64748B]">
          <span>{isUser ? "You" : "AURA"}</span>
          <span>·</span>
          <time dateTime={message.createdAt}>{formatTimestamp(message.createdAt)}</time>
        </div>
      </div>

      {isUser && (
        <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-[#7C5CFC]/30 bg-[#7C5CFC]/12 text-[#C4B5FD]">
          <User size={17} />
        </div>
      )}
    </article>
  );
}

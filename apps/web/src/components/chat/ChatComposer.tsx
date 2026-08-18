"use client";

import {
  Send,
  ShieldCheck,
} from "lucide-react";
import {
  forwardRef,
  type KeyboardEvent,
} from "react";

import Button from "@/components/ui/Button";

type ChatComposerProps = {
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
  onSend: () => void;
};

const ChatComposer = forwardRef<HTMLTextAreaElement, ChatComposerProps>(
  function ChatComposer({
    value,
    disabled,
    onChange,
    onSend,
  }, ref) {
    const canSend = value.trim().length > 0 && !disabled;

    function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
      if (event.key !== "Enter" || event.shiftKey) {
        return;
      }

      event.preventDefault();

      if (canSend) {
        onSend();
      }
    }

    return (
      <div className="rounded-2xl border border-[#1D2942] bg-[#0D1321]/95 p-3 shadow-2xl shadow-black/20 backdrop-blur-xl">
        <label htmlFor="aura-chat-composer" className="sr-only">
          Message AURA or describe a task
        </label>
        <textarea
          ref={ref}
          id="aura-chat-composer"
          aria-label="Message AURA or describe a task"
          value={value}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={3}
          placeholder="Message AURA or describe a task..."
          className="max-h-48 min-h-24 w-full resize-none rounded-xl border border-[#162036] bg-[#0A1020] px-4 py-3 text-sm leading-6 text-[#F8FAFC] outline-none transition placeholder:text-[#64748B] focus:border-[#7C5CFC]/60 disabled:opacity-60"
        />

        <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2 text-xs text-[#64748B]">
            <ShieldCheck size={14} className="text-[#2DD4BF]" />
            <span>AURA may create plans, use tools, and perform autonomous actions.</span>
          </div>

          <Button
            onClick={onSend}
            disabled={!canSend}
            aria-label="Send message to AURA"
            className="h-9 w-full px-3 sm:w-auto"
          >
            <Send size={16} />
            Send
          </Button>
        </div>
      </div>
    );
  },
);

export default ChatComposer;

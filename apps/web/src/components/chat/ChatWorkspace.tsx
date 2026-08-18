"use client";

import {
  BrainCircuit,
  CheckCircle2,
  MessageSquarePlus,
  Search,
  Sparkles,
  Trash2,
  Wrench,
} from "lucide-react";
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import BackendStatus from "@/components/system/BackendStatus";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import {
  runAura,
} from "@/lib/api/chat";
import type {
  AuraRunResponse,
} from "@/types/api";
import type {
  ChatMessage as ChatMessageType,
} from "@/types/chat";

import ChatComposer from "./ChatComposer";
import ChatMessage from "./ChatMessage";

const CHAT_SESSION_KEY = "aura-chat-session";

const suggestions = [
  {
    title: "Analyze system health",
    description: "Check AURA's current system health and summarize any issues.",
    icon: CheckCircle2,
  },
  {
    title: "Plan a software project",
    description: "Create a structured implementation plan for a REST API.",
    icon: BrainCircuit,
  },
  {
    title: "Inspect available tools",
    description: "Show me which tools are available and what they can do.",
    icon: Wrench,
  },
  {
    title: "Review stored context",
    description: "Summarize the useful information currently stored in memory.",
    icon: Search,
  },
];

function createMessageId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }

  return `message-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function nowIso() {
  return new Date().toISOString();
}

function readStoredMessages(): ChatMessageType[] {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const raw = window.sessionStorage.getItem(CHAT_SESSION_KEY);

    if (!raw) {
      return [];
    }

    const parsed = JSON.parse(raw) as unknown;

    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.filter(isStoredMessage);
  } catch {
    window.sessionStorage.removeItem(CHAT_SESSION_KEY);
    return [];
  }
}

function isStoredMessage(value: unknown): value is ChatMessageType {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const candidate = value as Partial<ChatMessageType>;

  return (
    typeof candidate.id === "string" &&
    typeof candidate.role === "string" &&
    ["user", "assistant", "system"].includes(candidate.role) &&
    typeof candidate.content === "string" &&
    typeof candidate.createdAt === "string" &&
    typeof candidate.status === "string" &&
    ["sending", "sent", "thinking", "completed", "error"].includes(candidate.status)
  );
}

function extractAssistantContent(response: AuraRunResponse) {
  if (!response.success) {
    throw new Error(response.message || "AURA could not complete this request.");
  }

  const result = response.result?.trim();

  if (result) {
    return result;
  }

  if (response.message.trim()) {
    return response.message;
  }

  throw new Error("AURA returned an empty response.");
}

function requestErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message;
  }

  if (typeof error === "string") {
    return error;
  }

  return "A network or response error interrupted the request.";
}

export default function ChatWorkspace() {
  const [messages, setMessages] = useState<ChatMessageType[]>(readStoredMessages);
  const [composerValue, setComposerValue] = useState("");
  const [requestActive, setRequestActive] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const composerRef = useRef<HTMLTextAreaElement | null>(null);
  const lastMessageCountRef = useRef(messages.length);

  const hasMessages = messages.length > 0;

  const lastUserPrompt = useMemo(() => {
    return [...messages].reverse().find((message) => message.role === "user")?.content ?? "";
  }, [messages]);

  useEffect(() => {
    try {
      if (messages.length === 0) {
        window.sessionStorage.removeItem(CHAT_SESSION_KEY);
      } else {
        window.sessionStorage.setItem(CHAT_SESSION_KEY, JSON.stringify(messages));
      }
    } catch {
      // Session persistence is a convenience; the chat should keep working without it.
    }
  }, [messages]);

  useEffect(() => {
    if (messages.length <= lastMessageCountRef.current) {
      lastMessageCountRef.current = messages.length;
      return;
    }

    lastMessageCountRef.current = messages.length;
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages.length]);

  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      const shouldFocus = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k";

      if (!shouldFocus) {
        return;
      }

      event.preventDefault();
      composerRef.current?.focus();
    }

    window.addEventListener("keydown", handleShortcut);

    return () => window.removeEventListener("keydown", handleShortcut);
  }, []);

  const sendPrompt = useCallback(async (prompt: string) => {
    const trimmedPrompt = prompt.trim();

    if (!trimmedPrompt || requestActive) {
      return;
    }

    const userMessage: ChatMessageType = {
      id: createMessageId(),
      role: "user",
      content: trimmedPrompt,
      createdAt: nowIso(),
      status: "sent",
    };
    const thinkingMessageId = createMessageId();
    const thinkingMessage: ChatMessageType = {
      id: thinkingMessageId,
      role: "assistant",
      content: "AURA is working...",
      createdAt: nowIso(),
      status: "thinking",
    };

    setComposerValue("");
    setRequestActive(true);
    setMessages((currentMessages) => [...currentMessages, userMessage, thinkingMessage]);

    try {
      const response = await runAura({
        message: trimmedPrompt,
      });
      const assistantContent = extractAssistantContent(response);

      setMessages((currentMessages) =>
        currentMessages.map((message) => {
          if (message.id !== thinkingMessageId) {
            return message;
          }

          return {
            id: message.id,
            role: "assistant",
            content: assistantContent,
            createdAt: nowIso(),
            status: "completed",
            metadata: {
              provider: response.provider,
              model: response.model,
              usedFallback: response.used_fallback,
            },
          };
        }),
      );
    } catch (error) {
      const detail = requestErrorMessage(error);

      setMessages((currentMessages) =>
        currentMessages.map((message) => {
          if (message.id !== thinkingMessageId) {
            return message;
          }

          return {
            id: message.id,
            role: "assistant",
            content: "AURA couldn't complete this request.",
            createdAt: nowIso(),
            status: "error",
            metadata: {
              retryPrompt: trimmedPrompt,
              errorDetail: detail,
            },
          };
        }),
      );
    } finally {
      setRequestActive(false);
    }
  }, [requestActive]);

  function handleSend() {
    void sendPrompt(composerValue);
  }

  function handleRetry(prompt: string) {
    void sendPrompt(prompt);
  }

  function handleNewChat() {
    if (messages.length > 0) {
      const confirmed = window.confirm("Clear this chat view? AURA memory and backend data will not be deleted.");

      if (!confirmed) {
        return;
      }
    }

    setMessages([]);
    setComposerValue("");
    window.sessionStorage.removeItem(CHAT_SESSION_KEY);
    window.setTimeout(() => composerRef.current?.focus(), 0);
  }

  return (
    <div className="mx-auto flex min-h-[calc(100vh-126px)] w-full max-w-5xl flex-col gap-5">
      <header className="rounded-[20px] border border-[#1D2942] bg-[#0D1321]/78 p-5 shadow-2xl shadow-black/20 sm:p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <Badge variant="purple">AURA Chat</Badge>
              <Badge variant="info">Runtime channel</Badge>
            </div>
            <h1 className="text-2xl font-semibold tracking-tight text-[#F8FAFC] sm:text-3xl">AURA Chat</h1>
            <p className="mt-2 text-sm text-[#94A3B8]">Direct interaction with the autonomous runtime</p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <BackendStatus />
            <Button variant="secondary" onClick={handleNewChat} disabled={requestActive && !hasMessages}>
              {hasMessages ? <Trash2 size={16} /> : <MessageSquarePlus size={16} />}
              New Chat
            </Button>
          </div>
        </div>
      </header>

      <main className="flex flex-1 flex-col gap-5">
        <div className="flex-1 rounded-[20px] border border-[#162036] bg-[#070B14]/35 p-4 sm:p-5">
          {!hasMessages ? (
            <EmptyState onPickSuggestion={setComposerValue} />
          ) : (
            <div className="flex flex-col gap-5" aria-live="polite" aria-relevant="additions">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  onRetry={handleRetry}
                  requestActive={requestActive}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="sticky bottom-4">
          <ChatComposer
            ref={composerRef}
            value={composerValue}
            disabled={requestActive}
            onChange={setComposerValue}
            onSend={handleSend}
          />
          {lastUserPrompt && requestActive && (
            <p className="mt-2 px-2 text-xs text-[#64748B]" role="status">
              AURA is processing your latest request.
            </p>
          )}
        </div>
      </main>
    </div>
  );
}

function EmptyState({
  onPickSuggestion,
}: {
  onPickSuggestion: (value: string) => void;
}) {
  return (
    <div className="flex min-h-[470px] flex-col items-center justify-center px-2 py-10 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#7C5CFC] text-white shadow-xl shadow-[#7C5CFC]/20">
        <Sparkles size={24} />
      </div>

      <h2 className="mt-5 text-3xl font-semibold tracking-tight text-[#F8FAFC]">What should we work on?</h2>
      <p className="mt-3 max-w-xl text-sm leading-6 text-[#94A3B8]">
        Give AURA a goal, ask a question, or describe a task you want the system to handle.
      </p>

      <div className="mt-8 grid w-full max-w-3xl gap-3 sm:grid-cols-2">
        {suggestions.map(({ title, description, icon: Icon }) => (
          <button
            key={title}
            type="button"
            onClick={() => onPickSuggestion(description)}
            className="aura-card aura-card-hover group p-4 text-left outline-none focus:border-[#7C5CFC]/70"
          >
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[#26334D] bg-[#111A2E] text-[#9B87FF] transition group-hover:border-[#7C5CFC]/50">
                <Icon size={18} />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-[#F8FAFC]">{title}</h3>
                <p className="mt-1 text-xs leading-5 text-[#94A3B8]">{description}</p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

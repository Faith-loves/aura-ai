export type ChatRole = "user" | "assistant" | "system";

export type ChatMessageStatus =
  | "sending"
  | "sent"
  | "thinking"
  | "completed"
  | "error";

export type ChatMessageMetadata = {
  provider?: string | null;
  model?: string | null;
  usedFallback?: boolean;
  retryPrompt?: string;
  errorDetail?: string;
};

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
  status: ChatMessageStatus;
  metadata?: ChatMessageMetadata;
};

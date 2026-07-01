import {
  AssistantRuntimeProvider,
  type AppendMessage,
  type ThreadMessageLike,
  useExternalStoreRuntime,
} from "@assistant-ui/react";
import { type ReactNode, useCallback, useState } from "react";

import { useSessionId } from "@/hooks/use-session-id";
import { ask, askStream } from "@/lib/api/ask";
import { ApiError } from "@/lib/api/client";
import { useSourceStore } from "@/stores/source-store";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  error?: string;
};

function generateId(): string {
  return crypto.randomUUID();
}

function convertMessage(message: ChatMessage): ThreadMessageLike {
  return {
    id: message.id,
    role: message.role,
    content: [{ type: "text", text: message.content }],
    ...(message.error
      ? { status: { type: "incomplete" as const, reason: "error" as const } }
      : {}),
  };
}

function getUserText(message: AppendMessage): string {
  const part = message.content[0];
  if (!part || part.type !== "text") {
    throw new Error("Only text messages are supported");
  }
  return part.text;
}

export function ChatProvider({ children }: { children: ReactNode }) {
  const sessionId = useSessionId();
  const setSources = useSourceStore((s) => s.setSources);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const onNew = useCallback(
    async (message: AppendMessage) => {
      const question = getUserText(message).trim();
      if (!question) return;

      const userId = generateId();
      setMessages((prev) => [
        ...prev,
        { id: userId, role: "user", content: question },
      ]);

      const assistantId = generateId();
      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: "assistant", content: "" },
      ]);

      setIsRunning(true);

      try {
        const request = { question, session_id: sessionId, top_k: 5 };

        for await (const token of askStream(request)) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: m.content + token }
                : m,
            ),
          );
        }

        const response = await ask(request);
        setSources(assistantId, response.sources);
      } catch (error) {
        const errorMessage =
          error instanceof ApiError
            ? `Request failed (${error.status}). Please try again.`
            : error instanceof Error
              ? error.message
              : "Something went wrong. Please try again.";

        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: errorMessage, error: errorMessage }
              : m,
          ),
        );
      } finally {
        setIsRunning(false);
      }
    },
    [sessionId, setSources],
  );

  const runtime = useExternalStoreRuntime({
    isRunning,
    messages,
    convertMessage,
    onNew,
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {children}
    </AssistantRuntimeProvider>
  );
}

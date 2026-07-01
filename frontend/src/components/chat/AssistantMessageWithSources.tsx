import {
  ErrorPrimitive,
  MessagePrimitive,
  useAuiState,
} from "@assistant-ui/react";
import type { FC } from "react";

import { MarkdownText } from "@/components/assistant-ui/markdown-text";
import { SourceList } from "@/components/chat/SourceList";
import { EMPTY_SOURCES, useSourceStore } from "@/stores/source-store";

export const AssistantMessageWithSources: FC = () => {
  const messageId = useAuiState((s) => s.message.id);
  const sources = useSourceStore(
    (s) => s.sourcesByMessageId[messageId ?? ""] ?? EMPTY_SOURCES,
  );

  return (
    <MessagePrimitive.Root
      data-slot="aui_assistant-message-root"
      data-role="assistant"
      className="fade-in slide-in-from-bottom-1 animate-in relative duration-150"
    >
      <div className="aui-assistant-message-content text-foreground max-w-[calc(var(--thread-max-width)*0.9)] px-2.5 leading-relaxed break-words">
        <MessagePrimitive.Parts
          components={{
            Text: MarkdownText,
          }}
        />
        <MessagePrimitive.Error>
          <ErrorPrimitive.Root className="border-destructive bg-destructive/10 text-destructive mt-2 rounded-md border p-3 text-sm">
            <ErrorPrimitive.Message />
          </ErrorPrimitive.Root>
        </MessagePrimitive.Error>
        <SourceList sources={sources} />
      </div>
    </MessagePrimitive.Root>
  );
};

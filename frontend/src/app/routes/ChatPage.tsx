import { Thread } from "@/components/assistant-ui/thread";
import { AssistantMessageWithSources } from "@/components/chat/AssistantMessageWithSources";
import { ChatWelcome } from "@/components/chat/ChatWelcome";
import { ChatProvider } from "@/hooks/use-chat-runtime";

export function ChatPage() {
  return (
    <ChatProvider>
      <div className="flex h-[calc(100vh-5.5rem)] flex-col">
        <Thread
          components={{
            Welcome: ChatWelcome,
            AssistantMessage: AssistantMessageWithSources,
          }}
        />
      </div>
    </ChatProvider>
  );
}

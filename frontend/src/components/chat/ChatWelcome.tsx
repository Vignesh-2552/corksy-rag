import type { FC } from "react";

const CorksyWelcome: FC = () => {
  return (
    <div className="aui-thread-welcome flex flex-col items-center justify-center gap-2 px-4 py-8 text-center">
      <h2 className="text-foreground text-2xl font-semibold">
        How can I help you today?
      </h2>
      <p className="text-muted-foreground max-w-md text-sm">
        Ask a question about your uploaded documents. Answers are generated from
        your indexed content with source citations.
      </p>
    </div>
  );
};

export const ChatWelcome = CorksyWelcome;

import type { ReactNode } from "react";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-border bg-background/95 supports-[backdrop-filter]:bg-background/80 sticky top-0 z-10 border-b backdrop-blur">
        <div className="mx-auto flex h-14 w-full max-w-5xl items-center px-4">
          <div className="flex items-center gap-2">
            <span className="bg-primary text-primary-foreground flex size-8 items-center justify-center rounded-lg text-sm font-semibold">
              C
            </span>
            <div>
              <h1 className="text-sm font-semibold leading-none">Corksy RAG</h1>
              <p className="text-muted-foreground text-xs">
                Ask questions about your documents
              </p>
            </div>
          </div>
        </div>
      </header>
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-4 py-4">
        {children}
      </main>
    </div>
  );
}

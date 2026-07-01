import { useCallback, useState } from "react";

const STORAGE_KEY = "corksy-session-id";

function createSessionId(): string {
  return crypto.randomUUID();
}

export function useSessionId(): string {
  const [sessionId] = useState(() => {
    const existing = sessionStorage.getItem(STORAGE_KEY);
    if (existing) return existing;
    const id = createSessionId();
    sessionStorage.setItem(STORAGE_KEY, id);
    return id;
  });

  return sessionId;
}

export function useResetSession(): () => void {
  return useCallback(() => {
    sessionStorage.removeItem(STORAGE_KEY);
    window.location.reload();
  }, []);
}

import { create } from "zustand";

import type { SourceReference } from "@/lib/api/types";

const EMPTY_SOURCES: SourceReference[] = [];

export { EMPTY_SOURCES };

interface SourceStore {
  sourcesByMessageId: Record<string, SourceReference[]>;
  setSources: (messageId: string, sources: SourceReference[]) => void;
  clear: () => void;
}

export const useSourceStore = create<SourceStore>((set) => ({
  sourcesByMessageId: {},
  setSources: (messageId, sources) =>
    set((state) => ({
      sourcesByMessageId: {
        ...state.sourcesByMessageId,
        [messageId]: sources,
      },
    })),
  clear: () => set({ sourcesByMessageId: {} }),
}));

## Context

corksy-rag is a FastAPI + LangGraph RAG backend with two question-answering endpoints:

| Endpoint | Protocol | Response |
|---|---|---|
| `POST /api/v1/ask` | JSON | Full answer + `sources[]` + `session_id` |
| `POST /api/v1/ask/stream` | SSE (`text/event-stream`) | Token chunks as `data: <token>\n\n`, ends with `data: [DONE]\n\n` |

There is currently no frontend. The user wants a chat page built with `@assistant-ui/react` — a composable React library for production chat UIs — with a clean folder structure and Vite build pipeline.

The backend does **not** expose a LangGraph SDK or Vercel AI SDK endpoint, so the frontend cannot use `@assistant-ui/react-langgraph` or `@assistant-ui/react-ai-sdk` out of the box. A custom runtime adapter is required.

## Goals / Non-Goals

**Goals:**
- Scaffold `frontend/` as a Vite + React 19 + TypeScript app
- Build a `/chat` page using assistant-ui primitives with the official shadcn/ui theme
- Stream answers from `/api/v1/ask/stream` via a custom `ExternalStoreRuntime` adapter
- Fetch source citations from `/api/v1/ask` after streaming completes (or in parallel)
- Establish a canonical `frontend/src/` layout documented in CONTRIBUTING.md
- Enable local dev with API proxy (Vite dev server → FastAPI on `:8000`)
- Add CORS middleware to FastAPI for cross-origin dev requests

**Non-Goals:**
- Multi-thread / conversation history sidebar (single session per tab for v1)
- User authentication or admin UI
- Document upload UI (backend `/upload` endpoint exists but is out of scope)
- Replacing or modifying the LangGraph agent logic
- Server-side rendering (SSR) — static SPA is sufficient
- Docker compose changes for frontend (document manual dev workflow; compose update is a follow-up)

## Decisions

### D1 — Vite + React SPA in `frontend/`

**Decision:** Use Vite with the React + TypeScript template. Place the app at `frontend/` in the monorepo root.

**Rationale:** Vite provides fast HMR, simple `npm run build` output to `dist/`, and built-in dev proxy. A separate package keeps Node dependencies isolated from the Python backend. Next.js is heavier than needed for a single chat page SPA.

**Alternative considered:** Next.js — better for SSR/SEO but unnecessary for an internal RAG chat tool; adds complexity.

---

### D2 — Custom `ExternalStoreRuntime` for SSE backend

**Decision:** Use `@assistant-ui/react`'s `useExternalStoreRuntime` to bridge the custom FastAPI SSE endpoint. Implement `onNew` to POST to `/api/v1/ask/stream`, parse SSE chunks, and append tokens to the assistant message. After stream completes, call `/api/v1/ask` to attach source metadata.

**Rationale:** The backend speaks raw SSE, not AI SDK or LangGraph wire protocol. `ExternalStoreRuntime` gives full control over message state while still using assistant-ui's `Thread`/`Composer`/`Message` components.

**Alternative considered:** `@assistant-ui/react-langgraph` — requires LangGraph Cloud/SDK thread API on the backend; not available today.

**Alternative considered:** `@assistant-ui/react-ai-sdk` — requires refactoring backend to AI SDK streaming format; too invasive.

---

### D3 — Folder structure

**Decision:** Adopt this layout:

```
frontend/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
├── index.html
├── .env.example
├── public/
└── src/
    ├── app/
    │   ├── main.tsx          # ReactDOM.createRoot entry
    │   ├── App.tsx           # Router shell
    │   ├── index.css         # Tailwind directives + CSS variables
    │   └── routes/
    │       └── ChatPage.tsx  # /chat page
    ├── components/
    │   ├── assistant-ui/     # CLI-copied primitives (thread, composer, etc.)
    │   ├── layout/
    │   │   └── AppShell.tsx  # Header, container, footer
    │   └── chat/
    │       └── SourceList.tsx # Renders SourceReference cards
    ├── hooks/
    │   ├── use-chat-runtime.ts   # ExternalStoreRuntime wiring
    │   └── use-session-id.ts     # sessionStorage UUID
    └── lib/
        ├── api/
        │   ├── client.ts     # fetch wrapper with base URL
        │   ├── ask.ts        # ask() and askStream() functions
        │   └── types.ts      # AskRequest, AskResponse, SourceReference
        └── sse.ts            # SSE line parser utility
```

**Rationale:** Mirrors the backend's layered separation (`api/` = HTTP, `hooks/` = state, `components/` = UI). Assistant-ui primitives are isolated so CLI updates don't mix with app-specific components.

---

### D4 — Assistant-ui setup via CLI + shadcn registry

**Decision:** Initialize components using:

```bash
cd frontend
npx assistant-ui@latest init
# or: npx shadcn@latest add https://r.assistant-ui.com/thread.json
```

Copy generated `thread.tsx`, `thread-list.tsx`, `markdown-text.tsx`, and supporting shadcn/ui components into `src/components/assistant-ui/`.

**Rationale:** Official path ensures compatible versions of `@assistant-ui/react`, `@assistant-ui/react-markdown`, and shadcn/ui primitives.

---

### D5 — Vite dev proxy for API calls

**Decision:** Configure `vite.config.ts` proxy:

```ts
server: {
  proxy: {
    '/api': { target: 'http://localhost:8000', changeOrigin: true }
  }
}
```

Use `VITE_API_BASE_URL=""` in dev (relative URLs hit the proxy) and `VITE_API_BASE_URL="http://localhost:8000"` for production or direct calls.

**Rationale:** Avoids CORS issues in development without requiring backend changes for the common local workflow. CORS middleware is still added for non-proxied scenarios.

---

### D6 — FastAPI CORS middleware

**Decision:** Add `CORSMiddleware` to `app/main.py` allowing `http://localhost:5173` (Vite default) in development, configurable via `CORS_ORIGINS` env var.

**Rationale:** Enables direct API calls when proxy is not used (e.g., deployed frontend on a different port).

---

### D7 — Session ID via sessionStorage

**Decision:** Generate a UUID on first message, persist in `sessionStorage` under key `corksy-session-id`. Reuse across page refreshes within the same tab.

**Rationale:** Matches backend `AskRequest.session_id` contract. `sessionStorage` scopes to tab (appropriate for v1 single-conversation UX).

## Risks / Trade-offs

- **SSE parsing complexity** → Mitigation: implement a tested `parseSSEStream()` utility in `lib/sse.ts`; handle partial chunks and `[DONE]` sentinel
- **Sources not available during stream** → Mitigation: show sources in a collapsible panel below the message after calling `/api/v1/ask` post-stream; accept brief delay
- **Duplicate API call** (stream + sync) → Trade-off: stream endpoint doesn't return sources today; a follow-up backend change could add sources to stream metadata
- **assistant-ui version drift** → Mitigation: pin versions in `package.json`; document upgrade path in CONTRIBUTING.md
- **No conversation history UI** → Acceptable for v1; `ThreadList` component can be added later when backend supports multi-session

## Migration Plan

1. Scaffold `frontend/` with Vite React-TS template
2. Install assistant-ui, Tailwind, shadcn/ui dependencies
3. Run assistant-ui CLI to copy component primitives
4. Implement API client, SSE parser, custom runtime hook
5. Build `ChatPage` with `AssistantRuntimeProvider` + `Thread`
6. Add CORS to FastAPI backend
7. Add `frontend/.env.example` and update CONTRIBUTING.md
8. Verify: `npm run dev` + `uvicorn main:app` → chat streams answers with sources

**Rollback:** Delete `frontend/` directory and revert CORS change — no backend API changes.

## Open Questions

- Should the backend `/ask/stream` endpoint be extended to include `sources` in a final SSE event to avoid the duplicate `/ask` call?
- Should production serve `frontend/dist/` from FastAPI static files, or deploy frontend separately (e.g., Vercel, S3)?
- Is a dark mode toggle required for v1, or is light mode sufficient?

## 1. Frontend Scaffold

- [x] 1.1 Create `frontend/` with Vite React + TypeScript template (`npm create vite@latest frontend -- --template react-ts`)
- [x] 1.2 Add `tailwind.config.ts`, `postcss.config.js`, and `src/app/index.css` with Tailwind directives and shadcn CSS variables
- [x] 1.3 Configure `tsconfig.json` path aliases (`@/` → `src/`) and update `vite.config.ts` to resolve them
- [x] 1.4 Add `frontend/.env.example` with `VITE_API_BASE_URL=http://localhost:8000`
- [x] 1.5 Configure Vite dev proxy: `/api` → `http://localhost:8000`
- [x] 1.6 Add npm scripts: `dev`, `build`, `preview`, `typecheck` (`tsc --noEmit`)

## 2. Assistant-ui Setup

- [x] 2.1 Install dependencies: `@assistant-ui/react`, `@assistant-ui/react-markdown`, `class-variance-authority`, `tailwind-merge`, `clsx`, `lucide-react`, `remark-gfm`, `zustand`
- [x] 2.2 Run `npx assistant-ui@latest init` (or shadcn registry add) to copy thread primitives into `src/components/assistant-ui/`
- [x] 2.3 Install shadcn/ui base components required by assistant-ui (`button`, `tooltip`, `avatar`, `dialog`, etc.) under `src/components/ui/`
- [x] 2.4 Verify assistant-ui components render without errors in a minimal test page

## 3. API Client Layer

- [x] 3.1 Create `src/lib/api/types.ts` with `AskRequest`, `AskResponse`, and `SourceReference` TypeScript interfaces matching backend schemas
- [x] 3.2 Create `src/lib/api/client.ts` — fetch wrapper that reads `VITE_API_BASE_URL` and sets JSON headers
- [x] 3.3 Create `src/lib/api/ask.ts` with `ask(request)` calling `POST /api/v1/ask` and returning parsed JSON
- [x] 3.4 Create `src/lib/sse.ts` with `parseSSEStream(response)` async generator yielding token strings from `data:` lines
- [x] 3.5 Create `src/lib/api/ask.ts` `askStream(request)` calling `POST /api/v1/ask/stream` and yielding tokens via SSE parser

## 4. Chat Runtime & Hooks

- [x] 4.1 Create `src/hooks/use-session-id.ts` — generate UUID on first use, persist in `sessionStorage` under `corksy-session-id`
- [x] 4.2 Create `src/hooks/use-chat-runtime.ts` — wire `useExternalStoreRuntime` with `onNew` handler that streams from `askStream()` and fetches sources from `ask()` after completion
- [x] 4.3 Attach source metadata to assistant messages (custom message metadata or parallel state map keyed by message ID)

## 5. Chat Page UI

- [x] 5.1 Create `src/components/layout/AppShell.tsx` — page header with app title and responsive container
- [x] 5.2 Create `src/components/chat/SourceList.tsx` — render `SourceReference` cards (file name, score, snippet)
- [x] 5.3 Create `src/app/routes/ChatPage.tsx` — wrap `AssistantRuntimeProvider` + `Thread` + welcome empty state
- [x] 5.4 Wire `App.tsx` with React Router (`/chat` route, redirect `/` → `/chat`)
- [x] 5.5 Update `src/app/main.tsx` entry point to mount `App` with router
- [x] 5.6 Handle error states: display inline error message on API failure, disable composer while streaming

## 6. Backend CORS

- [x] 6.1 Add `CORSMiddleware` to `app/main.py` with configurable `CORS_ORIGINS` (default: `http://localhost:5173`)
- [x] 6.2 Add `CORS_ORIGINS` to `app/core/config.py` settings if not already present

## 7. Documentation & Verification

- [x] 7.1 Update `CONTRIBUTING.md` (or README) with `frontend/` folder layout and dev workflow (`npm run dev` + `uvicorn main:app`)
- [x] 7.2 Run `npm run build` inside `frontend/` and confirm `dist/` output with no TypeScript errors
- [x] 7.3 Manual smoke test: open `/chat`, send a question, verify streaming response and source citations display
- [x] 7.4 Manual smoke test: verify session ID persists across page refresh within the same tab

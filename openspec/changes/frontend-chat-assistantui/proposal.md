## Why

The corksy-rag backend exposes `/api/v1/ask` and `/api/v1/ask/stream`, but there is no user-facing interface — every interaction requires manual API calls. A dedicated chat page built with `@assistant-ui/react` gives users a production-grade conversational UI (streaming, markdown, auto-scroll) and establishes a clean frontend layer in the monorepo before more UI features are added.

## What Changes

- Scaffold a `frontend/` package using Vite + React + TypeScript (built with `npm run build`)
- Add a `/chat` page with assistant-ui primitives (`Thread`, `Composer`, `Message`) styled via the official shadcn/ui theme
- Wire a custom assistant-ui runtime that calls the existing FastAPI `/api/v1/ask/stream` SSE endpoint for token streaming and `/api/v1/ask` for source citations
- Establish a canonical frontend folder structure: `src/app/`, `src/components/assistant-ui/`, `src/lib/api/`, `src/hooks/`
- Add CORS configuration on the FastAPI backend so the dev frontend can reach the API
- Add root-level scripts/docs for running frontend and backend together locally
- Add `frontend/.env.example` with `VITE_API_BASE_URL` for API proxy configuration

## Capabilities

### New Capabilities

- `chat-frontend`: Chat page UI powered by `@assistant-ui/react` — streaming answers from the RAG backend, session management, source citation display, and responsive layout
- `frontend-structure`: Canonical folder layout, naming conventions, and placement rules for all frontend source, components, and API client code in the `frontend/` package

### Modified Capabilities

<!-- No existing main specs in openspec/specs/ — backend API contracts are unchanged -->

## Impact

- **New directory**: `frontend/` (Vite app, `package.json`, `tsconfig.json`, `src/` tree)
- **New dependencies**: `@assistant-ui/react`, `@assistant-ui/react-markdown`, Tailwind CSS, shadcn/ui components copied by assistant-ui CLI
- **Modified files**: `app/main.py` or `app/core/config.py` (CORS middleware), root `README.md` or `CONTRIBUTING.md` (frontend dev instructions)
- **No breaking changes** to existing API endpoints — frontend is purely additive
- **Build output**: `frontend/dist/` served statically or proxied in production (documented in design)

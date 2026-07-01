# Contributing to Corksy RAG

## Repository layout

```
corksy-rag/
├── app/                    # FastAPI backend (Python)
│   ├── api/v1/             # HTTP routers (ask, upload, health)
│   ├── agents/             # LangGraph workflow (nodes, prompts, graph)
│   ├── core/               # Config, DI container, logging
│   ├── db/                 # Qdrant client
│   ├── schemas/            # Pydantic request/response models
│   └── services/           # Domain logic (retrieval, generation, etc.)
├── frontend/               # Vite + React chat UI
├── tests/                  # pytest (unit/, integration/)
├── docker/                 # Dockerfile and docker-compose
└── openspec/               # Change proposals and specs
```

### Backend placement rules

| Layer | Location | Examples |
|---|---|---|
| HTTP routes | `app/api/v1/` | `ask.py`, `upload.py` |
| API contracts | `app/schemas/` | `request.py`, `response.py` |
| Business logic | `app/services/` | `retrieval.py`, `generation.py` |
| LangGraph | `app/agents/` | `graph.py`, `nodes/`, `prompts/` |
| Infrastructure | `app/core/` | `config.py`, `containers.py` |

### Frontend placement rules

| Layer | Location | Examples |
|---|---|---|
| App entry & routes | `frontend/src/app/` | `main.tsx`, `App.tsx`, `routes/ChatPage.tsx` |
| Assistant-ui primitives | `frontend/src/components/assistant-ui/` | `thread.tsx`, `markdown-text.tsx` |
| App-specific UI | `frontend/src/components/` | `layout/`, `chat/` |
| shadcn/ui base | `frontend/src/components/ui/` | `button.tsx`, `tooltip.tsx` |
| API client | `frontend/src/lib/api/` | `ask.ts`, `client.ts`, `types.ts` |
| Hooks | `frontend/src/hooks/` | `use-chat-runtime.tsx`, `use-session-id.ts` |
| Utilities | `frontend/src/lib/` | `utils.ts`, `sse.ts` |
| Client state | `frontend/src/stores/` | `source-store.ts` |

## Local development

### Backend

```bash
# From repo root — requires Qdrant and .env configured
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open [http://localhost:5173/chat](http://localhost:5173/chat).

In development, Vite proxies `/api` requests to `http://localhost:8000`, so `VITE_API_BASE_URL` can be left empty in `.env`.

### Run both together

1. Start Qdrant (e.g. `docker compose -f docker/docker-compose.yml up qdrant`)
2. Start the API: `uvicorn main:app --reload --port 8000`
3. Start the frontend: `cd frontend && npm run dev`

### Production build

```bash
cd frontend
npm run build    # outputs to frontend/dist/
npm run preview  # serve dist/ locally
```

Set `VITE_API_BASE_URL` to your API origin when the frontend is served separately from the backend.

## CORS

The backend allows origins listed in `CORS_ORIGINS` (default: `http://localhost:5173`). Add additional origins as a comma-separated list in `.env`:

```
CORS_ORIGINS=http://localhost:5173,https://my-app.example.com
```

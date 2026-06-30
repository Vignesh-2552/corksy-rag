## Context

The upload pipeline stores document chunks in Qdrant with 384-dim `all-MiniLM-L6-v2` vectors. The `QdrantRepository` and `HuggingFaceEmbeddings` are already wired in `containers.py`. What is missing is the other half of the RAG loop: a service that embeds a user question, retrieves relevant chunks, and generates a grounded answer via a pluggable LLM.

The system design specifies LangGraph as the orchestration layer, a `retrieve → generate` flow with a `fallback` branch, and SSE streaming for the answer. The LLM must be swappable via env vars with no code changes.

## Goals / Non-Goals

**Goals:**
- `POST /api/v1/ask` — synchronous JSON response with answer + sources
- `POST /api/v1/ask/stream` — SSE streaming response (token-by-token)
- LangGraph workflow: `retrieve` node → conditional edge → `generate` or `fallback` node
- `RetrievalService` — embed question with the same `HuggingFaceEmbeddings` model, search Qdrant top-K
- `GenerationService` — prompt construction + LLM call with streaming support
- `llm_factory` — builds a LangChain chat model from `LLM_PROVIDER` / `LLM_MODEL` / `LLM_API_KEY`
- All new services injected via `dependency-injector` container

**Non-Goals:**
- Chat history / multi-turn memory (stateless per request)
- Re-ranking or hybrid search (BM25 + vector)
- Auth/rate-limiting on `/ask`
- Changing the upload pipeline or Qdrant collection schema

## Decisions

### D1 — LangGraph over a plain chain

**Decision:** Use `StateGraph` with typed state (`RAGState`) and explicit node functions.

**Rationale:** The fallback branch (no docs found → graceful message) requires a conditional edge that is cleanest as a graph. A plain `RunnableSequence` would require an `if` inside a step, making it harder to extend later (e.g., adding a rewrite node). LangGraph is already a declared dependency in the system design.

**Alternative considered:** `RunnableLambda` chain with an inline conditional — simpler, but not extensible and doesn't match the system design intent.

---

### D2 — Reuse `HuggingFaceEmbeddings` singleton for query embedding

**Decision:** Inject the same `embeddings` singleton from the container into `RetrievalService`; call `embed_query()` for the user question.

**Rationale:** The question vector must use the same model and dimension (384) as the indexed chunks, or cosine similarity scores are meaningless. Reusing the container singleton avoids loading the model twice.

**Alternative considered:** A separate query-embedding service — unnecessary overhead with no benefit when the model is identical.

---

### D3 — `llm_factory` as a plain function, not a class

**Decision:** `build_llm(provider, model, api_key)` is a module-level function. The container wraps it in `providers.Singleton`.

**Rationale:** The factory's only job is to select and instantiate one of five LangChain chat models. A class adds no value here. The `dependency-injector` `Singleton` handles lifecycle.

---

### D4 — SSE streaming via `StreamingResponse` + async generator

**Decision:** The `/ask/stream` endpoint returns `StreamingResponse(media_type="text/event-stream")` fed by an async generator that calls `llm.astream()`.

**Rationale:** FastAPI's `StreamingResponse` is the standard pattern for SSE. LangChain chat models all expose `astream()`, making this provider-agnostic. No third-party SSE library needed.

---

### D5 — Synchronous `/ask` calls the same workflow, collects full answer

**Decision:** `/ask` calls `workflow.ainvoke(state)` and returns the completed `RAGState` as JSON. No separate code path.

**Rationale:** Reusing the same LangGraph graph for both sync and streaming avoids duplication. The streaming variant swaps `ainvoke` for `astream` and wraps tokens in SSE format.

## Risks / Trade-offs

- **Model download on cold start** — `HuggingFaceEmbeddings` downloads `all-MiniLM-L6-v2` on first use. The model is already cached from the upload flow so this only affects fresh containers. → Mitigation: pre-warm by calling `embeddings.embed_query("warmup")` in the lifespan hook.
- **LLM latency on sync `/ask`** — The synchronous endpoint blocks until the full answer is generated. For slow LLMs this can feel unresponsive. → Mitigation: document that `/ask/stream` is preferred for production use; the sync endpoint is a convenience for testing.
- **No session state** — Each request is independent; the LLM has no memory of prior questions. → Acceptable per Non-Goals; can be added later as a graph node.
- **Qdrant `search` returns up to `top_k` results** — If the collection is empty, `retrieved_docs` is an empty list and the fallback node fires. This is correct behaviour but should be covered by a test.

## Open Questions

- Should `top_k` be a per-request parameter (from `AskRequest`) or a global config default? → Design assumes both: `AskRequest.top_k` defaults to `settings.retrieval_top_k` (new config field, default `5`).
- Should source snippets be truncated in the response? → Yes, to 200 chars to keep the response payload small.

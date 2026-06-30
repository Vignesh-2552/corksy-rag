## 1. Config & Dependencies

- [x] 1.1 Add `langgraph` to `pyproject.toml` dependencies and run `uv add langgraph`
- [x] 1.2 Add `retrieval_top_k: int = 5` to `app/config.py` Settings

## 2. Pydantic Schemas

- [x] 2.1 Add `AskRequest` (question, session_id, top_k) to `app/models/request.py`
- [x] 2.2 Add `SourceReference` (doc_id, source_file, score, snippet) to `app/models/response.py`
- [x] 2.3 Add `AskResponse` (answer, sources, session_id) to `app/models/response.py`

## 3. LLM Factory

- [x] 3.1 Create `app/services/llm_factory.py` with `build_llm(provider, model, api_key)` function
- [x] 3.2 Implement match arms for `anthropic`, `openai`, `ollama`, `groq`, `google` providers
- [x] 3.3 Raise `ValueError` for unknown provider

## 4. LangGraph Workflow

- [x] 4.1 Create `app/workflow/state.py` with `RAGState` TypedDict (session_id, question, top_k, retrieved_docs, answer, sources)
- [x] 4.2 Create `app/workflow/nodes/retrieve.py` — embed question, search Qdrant top-K, populate `retrieved_docs`
- [x] 4.3 Create `app/workflow/nodes/generate.py` — build context prompt, call LLM, populate `answer` and `sources`
- [x] 4.4 Create `app/workflow/nodes/fallback.py` — set fixed fallback message, empty sources
- [x] 4.5 Create `app/workflow/graph.py` — define `StateGraph`, add nodes, add conditional edge after `retrieve`, compile to `rag_app`

## 5. Services

- [x] 5.1 Create `app/services/retrieval.py` with `RetrievalService(qdrant_repo, embeddings)` and `async search(question, top_k)` method
- [x] 5.2 Create `app/services/generation.py` with `GenerationService(llm)` and `async generate(question, docs)` + `astream(question, docs)` methods

## 6. API Endpoint

- [x] 6.1 Create `app/api/v1/ask.py` with `POST /ask` route (sync, returns `AskResponse`)
- [x] 6.2 Add `POST /ask/stream` route to `app/api/v1/ask.py` (SSE, `StreamingResponse`)
- [x] 6.3 Register `ask.router` in `main.py` under `/api/v1`

## 7. Dependency Injection

- [x] 7.1 Add `llm` singleton to `app/containers.py` using `build_llm` factory
- [x] 7.2 Add `retrieval_service` factory to `app/containers.py`
- [x] 7.3 Add `generation_service` factory to `app/containers.py`
- [x] 7.4 Add `rag_workflow` factory to `app/containers.py` (wraps compiled LangGraph app)
- [x] 7.5 Add `app.api.v1.ask` to container `wiring_config` modules

## 8. Lifespan Warm-up

- [x] 8.1 Add `embeddings.embed_query("warmup")` call in `main.py` lifespan to pre-load the HuggingFace model before first request

## Why

The upload pipeline is complete, but the system has no way to answer questions — there is no retrieval or generation layer. The retriever agent closes this gap by wiring Qdrant semantic search, a pluggable LLM, and a LangGraph workflow into two endpoints (`/ask` and `/ask/stream`), completing the RAG loop.

## What Changes

- Add `POST /api/v1/ask` — synchronous question-answering endpoint
- Add `POST /api/v1/ask/stream` — SSE streaming variant
- Add `RetrievalService` — embeds the question and searches Qdrant for top-K chunks
- Add `GenerationService` — constructs the prompt with retrieved context and calls the LLM
- Add `llm_factory.py` — builds a LangChain chat model from `LLM_PROVIDER` + `LLM_MODEL` env vars (Anthropic, OpenAI, Ollama, Groq, Google)
- Add LangGraph workflow with `retrieve → generate` path and `fallback` node when no docs are found
- Add `RAGState` TypedDict to carry state across workflow nodes
- Wire all new services into `containers.py`
- Add `AskRequest` / `AskResponse` / `SourceReference` Pydantic schemas

## Capabilities

### New Capabilities

- `question-answering`: Synchronous and streaming `/ask` endpoints powered by LangGraph RAG workflow — retrieve relevant chunks from Qdrant, generate an answer via a pluggable LLM, return answer + source references
- `rag-workflow`: LangGraph graph definition with `retrieve`, `generate`, and `fallback` nodes and conditional edge based on whether documents were found
- `llm-factory`: Provider-agnostic LLM builder — reads `LLM_PROVIDER` / `LLM_MODEL` / `LLM_API_KEY` from config and returns the correct LangChain chat model

### Modified Capabilities

- `document-upload`: No requirement changes — the existing upload spec is unchanged. The retriever agent is purely additive and reads from the same Qdrant collection.

## Impact

- **New files**: `app/api/v1/ask.py`, `app/workflow/graph.py`, `app/workflow/state.py`, `app/workflow/nodes/retrieve.py`, `app/workflow/nodes/generate.py`, `app/workflow/nodes/fallback.py`, `app/services/retrieval.py`, `app/services/generation.py`, `app/services/llm_factory.py`
- **Modified files**: `app/containers.py` (add LLM, retrieval, generation, workflow providers), `app/models/request.py`, `app/models/response.py`, `main.py` (register `/ask` router)
- **Dependencies**: `langgraph` (already in spec, add to `pyproject.toml`)
- **No breaking changes** to existing `/upload` or `/health` endpoints

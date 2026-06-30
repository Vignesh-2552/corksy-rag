# E-Commerce RAG Pipeline — System Design Document

## Overview

A simple RAG pipeline with two endpoints: upload documents into a Qdrant vector store, and ask questions that get answered using retrieved context from those documents. The LLM provider is pluggable — swap any supported model via config.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [System Components](#3-system-components)
4. [Data Flow](#4-data-flow)
5. [LangGraph Workflow](#5-langgraph-workflow)
6. [API Design](#6-api-design)
7. [Database Schema](#7-database-schema)
8. [Indexing Pipeline](#8-indexing-pipeline)
9. [Retrieval Strategy](#9-retrieval-strategy)
10. [Dependency Injection](#10-dependency-injection)
11. [Pluggable LLM](#11-pluggable-llm)
12. [Error Handling & Fallbacks](#12-error-handling--fallbacks)
13. [Folder Structure](#13-folder-structure)

---

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                   E-Commerce RAG System                  │
│                                                          │
│  ┌──────────┐    ┌────────────────────────────────────┐  │
│  │  Client  │───▶│         FastAPI Gateway             │  │
│  │ (Web/App)│    │                                    │  │
│  └──────────┘    │  POST /upload   POST /ask          │  │
│                  └──────────┬───────────┬─────────────┘  │
│                             │           │                 │
│                    ┌────────▼───┐  ┌────▼──────────────┐ │
│                    │  Indexing  │  │  LangGraph Agent   │ │
│                    │  Pipeline  │  │                    │ │
│                    │            │  │ retrieve → generate │ │
│                    └────────────┘  └────────────────────┘ │
│                          │               │                 │
│                    ┌─────▼───────────────▼──────────────┐ │
│                    │         Qdrant DB (Vector Store)    │ │
│                    └────────────────────────────────────┘ │
│                                          │                 │
│                                   ┌──────▼──────┐         │
│                                   │  LLM Model  │         │
│                                   │ (pluggable) │         │
│                                   └─────────────┘         │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| API Framework | **FastAPI** | Async REST API + SSE streaming |
| Orchestration | **LangGraph** | Stateful RAG agent workflow |
| LLM Framework | **LangChain** | Prompts, document loaders, chains |
| Vector Database | **Qdrant** | Semantic similarity search |
| Embeddings | **text-embedding-3-small** (OpenAI) | Document + query vectorization |
| LLM | **Pluggable** (see Section 11) | Answer generation |
| Async Runtime | **asyncio + uvicorn** | Non-blocking I/O |
| DI Container | **dependency-injector** | Service wiring & lifecycle |

---

## 3. System Components

### 3.1 Upload Service
Receives documents (PDF, TXT, JSON, CSV), splits them into chunks, embeds them, and upserts into Qdrant.

### 3.2 LangGraph Agent
Handles the question-answering workflow:

| Node | Responsibility |
|---|---|
| `retrieve` | Search Qdrant for relevant chunks |
| `generate` | Build prompt with context and call LLM |
| `fallback` | Return graceful message if no docs found |

### 3.3 Retrieval Service
Performs semantic search against Qdrant and returns top-K chunks.

### 3.4 Generation Service
Wraps the LLM call with prompt construction and streaming support. The LLM is injected via config — no hardcoded provider.

---

## 4. Data Flow

### 4.1 Upload Flow

```
Client uploads file(s)
        │
        ▼
[POST /upload]
        │  accept PDF / TXT / JSON / CSV
        ▼
[Document Loader] (LangChain)
        │
        ▼
[Text Splitter]  chunk_size=512, overlap=64
        │
        ▼
[Embeddings]  → OpenAI text-embedding-3-small
        │
        ▼
[Qdrant Upsert]  → collection: "documents"
        │
        ▼
{ "status": "indexed", "chunks": N }
```

### 4.2 Question Flow

```
Customer Question
        │
        ▼
[POST /ask]
        │
        ▼
[LangGraph: retrieve]  ──▶ Qdrant semantic search
        │  top-5 chunks
        ▼
[LangGraph: generate]  ──▶ LLM (pluggable)
        │  streamed answer tokens
        ▼
[SSE stream to client]
```

---

## 5. LangGraph Workflow

```python
class RAGState(TypedDict):
    session_id: str
    question: str
    retrieved_docs: list[Document]
    answer: str
    sources: list[str]
```

### Workflow Graph

```
START
  │
  ▼
retrieve  ──▶ Qdrant top-K search
  │
  ▼
 docs found?
  ├── YES ──▶ generate ──▶ END (stream answer)
  └── NO  ──▶ fallback ──▶ END ("No relevant documents found")
```

---

## 6. API Design

### Base URL: `/api/v1`

### 6.1 Endpoints

```
POST  /upload        # Upload and index documents
POST  /ask           # Ask a question (sync)
POST  /ask/stream    # Ask a question (SSE streaming)
GET   /health        # Liveness check
```

### 6.2 Schemas

```python
# POST /upload
# Content-Type: multipart/form-data
# Body: files[] — one or more files (PDF, TXT, JSON, CSV)

class UploadResponse(BaseModel):
    status: str          # "indexed"
    files: list[str]     # filenames processed
    chunks: int          # total chunks stored

# POST /ask
class AskRequest(BaseModel):
    question: str        # max 500 chars
    session_id: str
    top_k: int = 5       # number of chunks to retrieve

class AskResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    session_id: str

class SourceReference(BaseModel):
    doc_id: str
    title: str
    score: float
    snippet: str
```

---

## 7. Database Schema

### Qdrant Collection: `documents`

| Field | Type | Purpose |
|---|---|---|
| vector | float[1536] | Embedding of the chunk |
| `doc_id` | string | Unique chunk identifier |
| `source_file` | string | Original filename |
| `chunk_index` | int | Position within source file |
| `text` | string | Raw chunk text |
| `indexed_at` | datetime | When it was uploaded |

**Example payload:**
```json
{
  "doc_id": "faq_001_chunk_3",
  "source_file": "faq.pdf",
  "chunk_index": 3,
  "text": "Our return policy allows returns within 30 days...",
  "indexed_at": "2026-06-29T00:00:00Z"
}
```

---

## 8. Indexing Pipeline

```python
async def index_documents(files: list[UploadFile]) -> UploadResponse:
    all_chunks = []

    for file in files:
        # 1. Load by file type
        loader = get_loader(file)          # PDF / TXT / JSON / CSV
        docs = loader.load()

        # 2. Split
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=64,
        )
        chunks = splitter.split_documents(docs)
        all_chunks.extend(chunks)

    # 3. Embed in batches
    embeddings = await embed_in_batches(all_chunks, batch_size=100)

    # 4. Upsert to Qdrant
    await qdrant_client.upsert(
        collection_name="documents",
        points=build_points(all_chunks, embeddings),
    )

    return UploadResponse(
        status="indexed",
        files=[f.filename for f in files],
        chunks=len(all_chunks),
    )
```

### Supported Loaders

| File Type | LangChain Loader |
|---|---|
| PDF | `PyPDFLoader` |
| TXT | `TextLoader` |
| JSON | `JSONLoader` |
| CSV | `CSVLoader` |

---

## 9. Retrieval Strategy

Semantic search on the single `documents` collection:

```
Question
  │
  ▼
Embed question → float[1536]
  │
  ▼
Qdrant cosine similarity search → top-K chunks
  │
  ▼
Pass chunks as context to LLM
```

```python
async def retrieve(state: RAGState) -> RAGState:
    results = await qdrant_client.search(
        collection_name="documents",
        query_vector=await embed(state["question"]),
        limit=5,
        with_payload=True,
    )
    state["retrieved_docs"] = [
        Document(page_content=r.payload["text"], metadata=r.payload)
        for r in results
    ]
    return state
```

---

## 10. Dependency Injection

```python
# containers.py
class Container(containers.DeclarativeContainer):

    config = providers.Configuration()

    qdrant_client = providers.Singleton(
        AsyncQdrantClient,
        host=config.qdrant.host,
        port=config.qdrant.port,
        api_key=config.qdrant.api_key,
    )

    embeddings = providers.Singleton(
        OpenAIEmbeddings,
        model="text-embedding-3-small",
        api_key=config.openai.api_key,
    )

    llm = providers.Singleton(
        build_llm,              # factory — see Section 11
        provider=config.llm.provider,
        model=config.llm.model,
        api_key=config.llm.api_key,
    )

    retrieval_service = providers.Factory(
        RetrievalService,
        qdrant_client=qdrant_client,
        embeddings=embeddings,
    )

    generation_service = providers.Factory(
        GenerationService,
        llm=llm,
    )

    rag_workflow = providers.Factory(
        RAGWorkflow,
        retrieval_service=retrieval_service,
        generation_service=generation_service,
    )
```

```python
# FastAPI wiring
@router.post("/ask/stream")
@inject
async def ask_stream(
    request: AskRequest,
    workflow: RAGWorkflow = Depends(Provide[Container.rag_workflow]),
):
    return StreamingResponse(
        workflow.astream(request),
        media_type="text/event-stream",
    )
```

---

## 11. Pluggable LLM

Set `LLM_PROVIDER` and `LLM_MODEL` in `.env` to switch models without changing code.

### Supported Providers

| `LLM_PROVIDER` | `LLM_MODEL` examples | Notes |
|---|---|---|
| `anthropic` | `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `claude-opus-4-8` | Requires `ANTHROPIC_API_KEY` |
| `openai` | `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo` | Requires `OPENAI_API_KEY` |
| `google` | `gemini-1.5-pro`, `gemini-1.5-flash` | Requires `GOOGLE_API_KEY` |
| `ollama` | `llama3`, `mistral`, `phi3` | Local — no API key needed |
| `groq` | `llama-3.1-70b-versatile`, `mixtral-8x7b-32768` | Requires `GROQ_API_KEY` |

### LLM Factory

```python
# services/llm_factory.py
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

def build_llm(provider: str, model: str, api_key: str | None = None):
    match provider:
        case "anthropic":
            return ChatAnthropic(model=model, api_key=api_key, streaming=True)
        case "openai":
            return ChatOpenAI(model=model, api_key=api_key, streaming=True)
        case "google":
            return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
        case "ollama":
            return ChatOllama(model=model)   # no key needed
        case "groq":
            return ChatGroq(model=model, api_key=api_key)
        case _:
            raise ValueError(f"Unknown LLM provider: {provider}")
```

### System Prompt (shared across all providers)

```python
SYSTEM_PROMPT = """
You are a helpful e-commerce assistant.
Answer the customer's question using ONLY the context provided below.
If the answer is not in the context, say you don't know.

Context:
{context}
"""
```

---

## 12. Error Handling & Fallbacks

| Failure | Handling |
|---|---|
| No relevant docs found | Return "I couldn't find relevant information. Please contact support." |
| Qdrant unreachable | 503 response with clear error message |
| LLM API error | 502 response, log the error |
| Unsupported file type | 400 response with list of accepted types |
| File too large | 413 response (max file size configurable) |

```python
async def fallback(state: RAGState) -> RAGState:
    state["answer"] = (
        "I couldn't find relevant information for your question. "
        "Please contact our support team for help."
    )
    state["sources"] = []
    return state
```

---

## 13. Folder Structure

```
corksy-rag/
├── app/
│   ├── main.py                  # FastAPI app, DI wiring, lifespan
│   ├── containers.py            # dependency-injector Container
│   ├── config.py                # pydantic-settings config
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── upload.py        # POST /upload
│   │       ├── ask.py           # POST /ask  +  POST /ask/stream
│   │       └── health.py        # GET /health
│   │
│   ├── workflow/
│   │   ├── graph.py             # LangGraph graph definition
│   │   ├── state.py             # RAGState TypedDict
│   │   └── nodes/
│   │       ├── retrieve.py      # retrieve node
│   │       ├── generate.py      # generate node
│   │       └── fallback.py      # fallback node
│   │
│   ├── services/
│   │   ├── retrieval.py         # Qdrant search
│   │   ├── generation.py        # LLM call + streaming
│   │   ├── embedding.py         # Async batch embedding
│   │   ├── llm_factory.py       # Pluggable LLM builder
│   │   └── indexing.py          # Document load → chunk → embed → upsert
│   │
│   ├── db/
│   │   └── qdrant.py            # Qdrant client + collection setup
│   │
│   └── models/
│       ├── request.py           # Pydantic request schemas
│       └── response.py          # Pydantic response schemas
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml       # API + Qdrant
│
├── pyproject.toml
├── .env.example
└── SYSTEM_DESIGN.md
```

---

## Environment Variables

```env
# LLM — change provider + model to switch (no code change needed)
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-6
LLM_API_KEY=sk-ant-...

# Embeddings
OPENAI_API_KEY=sk-...

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=

# App
APP_ENV=development
MAX_FILE_SIZE_MB=50
LOG_LEVEL=INFO
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Two endpoints only** | Upload + Ask covers the full RAG loop; no extra complexity |
| **Single Qdrant collection** | One `documents` collection for all uploaded content; simple and sufficient |
| **Pluggable LLM via factory** | `LLM_PROVIDER` + `LLM_MODEL` in `.env` — swap Anthropic, OpenAI, Ollama, Groq without touching code |
| **LangGraph over plain chain** | Enables conditional fallback node if no docs are found; easy to extend later |
| **No PostgreSQL / Redis** | Not needed for core RAG; Qdrant stores all document data; sessions are stateless |
| **Async all the way** | FastAPI + AsyncQdrantClient + async LangChain calls for non-blocking throughput |

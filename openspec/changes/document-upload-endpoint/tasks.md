## 1. Project Setup

- [x] 1.1 Create the folder structure: `app/api/v1/`, `app/services/`, `app/db/`, `app/models/`, `app/workflow/`, `app/workflow/nodes/`
- [x] 1.2 Add dependencies to `pyproject.toml`: `fastapi`, `uvicorn`, `langchain`, `langchain-community`, `pypdf`, `openai`, `langchain-openai`, `qdrant-client[async]`, `dependency-injector`, `pydantic-settings`, `python-multipart`
- [x] 1.3 Create `.env.example` with all required environment variables (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`, `OPENAI_API_KEY`, `QDRANT_HOST`, `QDRANT_PORT`, `QDRANT_API_KEY`, `MAX_FILE_SIZE_MB`, `LOG_LEVEL`)
- [x] 1.4 Create `app/config.py` using `pydantic-settings` to load and validate all env vars

## 2. Qdrant Collection Setup

- [x] 2.1 Create `app/db/qdrant.py` with an `AsyncQdrantClient` factory and an async `ensure_collection()` function that creates the `documents` collection (`vector_size=1536`, `distance=Cosine`) if it does not already exist

## 3. Embedding Service

- [x] 3.1 Create `app/services/embedding.py` with an async `embed_in_batches(chunks, batch_size=100)` function that calls OpenAI `text-embedding-3-small` in batches of 100 using `asyncio.gather`

## 4. Indexing Service

- [x] 4.1 Create `app/services/indexing.py` with a `get_loader(file_path, extension)` factory that returns the correct LangChain loader (`PyPDFLoader`, `TextLoader`, `JSONLoader`, `CSVLoader`)
- [x] 4.2 In `indexing.py` implement `async index_documents(files)` that: saves each `UploadFile` to a temp file, loads it, splits with `RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)`, collects all chunks, calls `embed_in_batches`, builds Qdrant `PointStruct` objects with `doc_id = uuid5(source_file:chunk_index)`, upserts to `documents` collection, and cleans up temp files
- [x] 4.3 Add per-file validation in `index_documents`: reject unsupported extensions (HTTP 400) and files exceeding `MAX_FILE_SIZE_MB` (HTTP 413) before any processing

## 5. Request / Response Models

- [x] 5.1 Create `app/models/request.py` — not needed for upload (multipart, no JSON body); add `AskRequest` placeholder for future use
- [x] 5.2 Create `app/models/response.py` with `UploadResponse(status: str, files: list[str], chunks: int)` and `SourceReference` / `AskResponse` for future use

## 6. Upload API Router

- [x] 6.1 Create `app/api/v1/upload.py` with `POST /upload` endpoint that accepts `files: list[UploadFile]`, calls `indexing_service.index_documents(files)`, and returns `UploadResponse`
- [x] 6.2 Create `app/api/v1/health.py` with `GET /health` returning `{"status": "ok"}`

## 7. Dependency Injection Container

- [x] 7.1 Create `app/containers.py` with `dependency-injector` `DeclarativeContainer` that wires: `AsyncQdrantClient`, `OpenAIEmbeddings`, `IndexingService` (injecting qdrant client + embeddings)
- [x] 7.2 Add `@inject` decorator and `Provide[Container.indexing_service]` to the upload router

## 8. FastAPI App Entry Point

- [x] 8.1 Create `app/main.py` with FastAPI app, lifespan that calls `ensure_collection()` on startup, mounts the `upload` and `health` routers under `/api/v1`, and wires the DI container

## 9. Docker Compose

- [x] 9.1 Create `docker/docker-compose.yml` with two services: `api` (builds from `Dockerfile`) and `qdrant` (using `qdrant/qdrant` image with port 6333 exposed)
- [x] 9.2 Create `docker/Dockerfile` with Python 3.12 slim base, copies `app/` and `pyproject.toml`, installs dependencies, runs `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## 10. Verification

- [ ] 10.1 Start services with `docker compose up`, confirm Qdrant is reachable at `localhost:6333`
- [ ] 10.2 Upload a sample PDF via `curl -F "files=@sample.pdf" http://localhost:8000/api/v1/upload` and verify the JSON response contains `status: "indexed"` and a non-zero `chunks` count
- [ ] 10.3 Check Qdrant dashboard (`localhost:6333/dashboard`) to confirm the `documents` collection has points
- [ ] 10.4 Upload an unsupported file type and verify HTTP 400 is returned
- [ ] 10.5 Confirm `GET /health` returns HTTP 200


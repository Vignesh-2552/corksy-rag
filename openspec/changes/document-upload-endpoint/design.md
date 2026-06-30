## Context

The RAG pipeline (defined in SYSTEM_DESIGN.md) requires a Qdrant `documents` collection to be populated before the `/ask` endpoint can return meaningful answers. The `POST /upload` endpoint is the only ingestion path — it must handle PDF, TXT, JSON, and CSV files, chunk them, embed them via OpenAI, and upsert into Qdrant.

The system uses FastAPI with full async I/O, `dependency-injector` for service wiring, and `AsyncQdrantClient`. All upstream services (Qdrant, OpenAI) are accessed asynchronously.

## Goals / Non-Goals

**Goals:**
- Implement `POST /api/v1/upload` as a multipart file upload endpoint
- Build a loader factory that selects the correct LangChain loader by file extension
- Split documents with `RecursiveCharacterTextSplitter` (chunk_size=512, overlap=64)
- Embed in async batches of 100 using OpenAI `text-embedding-3-small`
- Upsert to Qdrant `documents` collection with full payload
- Wire the indexing service into the DI container

**Non-Goals:**
- Authentication / authorization on the upload endpoint (handled separately)
- Duplicate detection or re-indexing prevention
- Support for HTML, DOCX, or other file formats beyond the four specified
- Streaming progress updates during upload

## Decisions

### Decision 1: Save uploaded files to a temp path before loading

**Choice**: Write each `UploadFile` to a temp file on disk, pass the path to the LangChain loader, then delete it.

**Why**: All LangChain loaders (`PyPDFLoader`, `CSVLoader`, etc.) require a file path — they do not accept an in-memory stream. Writing to a temp file is the simplest, correct approach.

**Alternative considered**: Load raw bytes into `io.BytesIO` and wrap with a custom loader — rejected because it requires forking or monkeypatching LangChain loaders, adding fragile complexity.

### Decision 2: Async batch embedding with configurable batch size

**Choice**: Embed chunks in batches of 100 using `asyncio.gather` per batch, defaulting to batch size 100.

**Why**: OpenAI's embedding API has a token limit per request (~8191 tokens per input, up to 2048 inputs per batch). Batching at 100 chunks stays safely within limits and allows concurrent embedding for large documents.

**Alternative considered**: Embed all chunks in a single call — rejected because large documents can exceed API limits and cause silent truncation.

### Decision 3: Single `documents` Qdrant collection for all file types

**Choice**: All uploaded files — regardless of type — go into one collection named `documents`.

**Why**: Consistent with SYSTEM_DESIGN.md. The `/ask` endpoint searches a single collection; separating by file type would require routing logic in retrieval that isn't needed at this stage.

**Alternative considered**: Per-type collections (`products`, `faqs`, `policies`) — deferred to a future enhancement once intent classification is added.

### Decision 4: Generate `doc_id` as `{filename}_{chunk_index}` UUID hash

**Choice**: `doc_id = uuid5(NAMESPACE_URL, f"{source_file}:{chunk_index}")` — deterministic UUID from filename + chunk index.

**Why**: Deterministic IDs allow re-uploads to overwrite (upsert) existing chunks for the same file rather than creating duplicates. Qdrant upsert semantics match this pattern.

## Risks / Trade-offs

- **Large file memory pressure** → Files are streamed to disk via `UploadFile.read()` in chunks (64 KB). Temp files are deleted after upsert completes, including on error.
- **OpenAI API latency** → For large documents (1000+ chunks), embedding takes 10+ seconds. The endpoint is synchronous from the client's perspective. A future enhancement can make this async with a job ID response.
- **No deduplication** → Uploading the same file twice creates duplicate vectors. Deterministic `doc_id` + Qdrant upsert mitigates this — same chunks overwrite themselves.
- **Qdrant collection must pre-exist** → The `documents` collection is created at app startup via `app/db/qdrant.py`. If startup fails silently, uploads will return 503.

## Migration Plan

1. Create Qdrant `documents` collection at app startup (`vector_size=1536`, `distance=Cosine`)
2. Deploy the new `upload.py` router and `indexing.py` service
3. Wire into `containers.py` and register the router in `main.py`
4. Test with a sample PDF upload via curl or Swagger UI
5. No rollback needed — endpoint is additive; removing it has no side effects on existing data

## Open Questions

- Should there be a maximum total payload size (sum of all files in one request)? Currently only per-file size is validated.
- Should the response include per-file chunk counts or only the total?

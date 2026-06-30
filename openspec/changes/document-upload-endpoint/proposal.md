## Why

The e-commerce RAG pipeline needs a way to ingest knowledge documents (product catalogs, FAQs, return policies) so customers can ask questions and receive accurate answers. The `POST /upload` endpoint is the entry point for this indexing — without it, the Qdrant vector store remains empty and the `/ask` endpoint has nothing to retrieve from.

## What Changes

- Introduce a new `POST /upload` endpoint that accepts one or more files (PDF, TXT, JSON, CSV)
- Each uploaded file is loaded via a LangChain document loader, split into chunks, embedded, and upserted into the Qdrant `documents` collection
- A structured JSON response confirms how many files were indexed and how many chunks were stored
- A pluggable loader factory selects the correct LangChain loader based on file extension

## Capabilities

### New Capabilities

- `document-upload`: Accept multipart file uploads, run the load → chunk → embed → upsert pipeline, and return an indexed confirmation response

### Modified Capabilities

<!-- None — this is a net-new endpoint with no existing spec to modify -->

## Impact

- **New file**: `app/api/v1/upload.py` — FastAPI router for `POST /upload`
- **New file**: `app/services/indexing.py` — document load, split, embed, upsert logic
- **New file**: `app/services/embedding.py` — async batch embedding helper
- **Dependency**: `app/db/qdrant.py` — Qdrant client must have the `documents` collection pre-created
- **DI**: `containers.py` must wire `qdrant_client`, `embeddings`, and `indexing_service`
- **Dependencies added**: `pypdf`, `langchain-community`, `qdrant-client[async]`, `openai`

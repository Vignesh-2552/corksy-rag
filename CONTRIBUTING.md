# Contributing to corksy-rag

## Folder placement rules

When adding new code, place it in the layer that matches its responsibility:

| Layer | Path | What goes here |
|---|---|---|
| Bootstrap | `app/main.py` | FastAPI app factory, lifespan, router registration |
| Core | `app/core/` | Config, DI container, logging — no domain logic |
| API | `app/api/v1/` | HTTP routers — one file per endpoint group |
| Schemas | `app/schemas/` | Pydantic request/response models for the API |
| Services | `app/services/` | Business logic (embedding, indexing, retrieval, generation) |
| Workflow | `app/workflow/` | LangGraph state, graph, and nodes |
| Database | `app/db/` | External datastore clients (Qdrant) |
| Unit tests | `tests/unit/` | Tests with mocked external dependencies |
| Integration tests | `tests/integration/` | Tests hitting HTTP endpoints or real wiring |

## Conventions

- All internal imports use the `app.` package prefix (e.g. `from app.core.config import settings`).
- Every Python package directory must contain an `__init__.py`.
- API routers are registered in `app/main.py`, not in individual router files.
- Do not put business logic in routers — delegate to services or workflow nodes.

## Running locally

```bash
uvicorn main:app --reload
```

## Running tests

```bash
pytest
```

## Running with Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

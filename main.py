from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.containers import Container
from app.logger import get_logger, setup_logging

setup_logging()
log = get_logger("corksy.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    container = app.state.container

    log.info("Starting up — ensuring Qdrant collection exists")
    repo = container.qdrant_repo()
    await repo.ensure_collection()
    log.info("Qdrant collection ready")

    log.info("Pre-loading HuggingFace embedding model")
    embeddings = container.embeddings()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, embeddings.embed_query, "warmup")
    log.info("Embedding model loaded — app ready")

    yield
    log.info("Shutting down")


def create_app() -> FastAPI:
    container = Container()

    app = FastAPI(title="Corksy RAG API", version="0.1.0", lifespan=lifespan)
    app.state.container = container

    from app.api.v1 import ask, health, upload

    app.include_router(upload.router, prefix="/api/v1")
    app.include_router(ask.router, prefix="/api/v1")
    app.include_router(health.router, prefix="/api/v1")

    return app


app = create_app()

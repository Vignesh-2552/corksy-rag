from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.containers import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = app.state.container
    repo = container.qdrant_repo()
    await repo.ensure_collection()
    yield


def create_app() -> FastAPI:
    container = Container()

    app = FastAPI(title="Corksy RAG API", version="0.1.0", lifespan=lifespan)
    app.state.container = container

    from app.api.v1 import health, upload

    app.include_router(upload.router, prefix="/api/v1")
    app.include_router(health.router, prefix="/api/v1")

    return app


app = create_app()

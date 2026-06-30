from dependency_injector import containers, providers
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import AsyncQdrantClient

from app.config import settings
from app.db.qdrant import QdrantRepository
from app.services.indexing import IndexingService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.api.v1.upload"],
    )

    qdrant_client = providers.Singleton(
        AsyncQdrantClient,
        host=settings.qdrant_host,
        port=settings.qdrant_port,
    )

    qdrant_repo = providers.Singleton(
        QdrantRepository,
        client=qdrant_client,
        collection_name=settings.qdrant_collection_name,
        vector_size=settings.vector_size,
    )

    embeddings = providers.Singleton(
        HuggingFaceEmbeddings,
        model_name=settings.embedding_model,
    )

    indexing_service = providers.Factory(
        IndexingService,
        qdrant_repo=qdrant_repo,
        embeddings=embeddings,
    )

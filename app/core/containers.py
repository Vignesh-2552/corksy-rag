from dependency_injector import containers, providers
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import AsyncQdrantClient

from app.core.config import settings
from app.db.qdrant import QdrantRepository
from app.services.generation import GenerationService
from app.services.indexing import IndexingService
from app.services.llm_factory import build_llm
from app.services.retrieval import RetrievalService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.api.v1.upload", "app.api.v1.ask"],
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

    llm = providers.Singleton(
        build_llm,
        provider=settings.llm_provider,
        model=settings.llm_model,
        api_key=settings.llm_api_key,
    )

    indexing_service = providers.Factory(
        IndexingService,
        qdrant_repo=qdrant_repo,
        embeddings=embeddings,
    )

    retrieval_service = providers.Factory(
        RetrievalService,
        qdrant_repo=qdrant_repo,
        embeddings=embeddings,
    )

    generation_service = providers.Factory(
        GenerationService,
        llm=llm,
    )

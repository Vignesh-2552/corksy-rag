import asyncio

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.db.qdrant import QdrantRepository
from app.core.logger import get_logger

log = get_logger("corksy.retrieval")


class RetrievalService:
    def __init__(self, qdrant_repo: QdrantRepository, embeddings: Embeddings):
        self._qdrant = qdrant_repo
        self._embeddings = embeddings

    async def search(self, question: str, top_k: int) -> list[Document]:
        log.info("Retrieving top-%d docs for question: '%s'", top_k, question[:80])
        loop = asyncio.get_event_loop()
        query_vector = await loop.run_in_executor(None, self._embeddings.embed_query, question)

        results = await self._qdrant.search(query_vector=query_vector, top_k=top_k)
        log.info("Retrieved %d documents", len(results))

        return [
            Document(
                page_content=r.payload.get("text", ""),
                metadata={
                    "doc_id": r.payload.get("doc_id", ""),
                    "source_file": r.payload.get("source_file", ""),
                    "chunk_index": r.payload.get("chunk_index", 0),
                    "score": r.score,
                },
            )
            for r in results
        ]

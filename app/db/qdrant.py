from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.logger import get_logger

log = get_logger("corksy.qdrant")


class QdrantRepository:
    def __init__(self, client: AsyncQdrantClient, collection_name: str, vector_size: int):
        self._client = client
        self._collection_name = collection_name
        self._vector_size = vector_size

    async def ensure_collection(self) -> None:
        existing = await self._client.get_collections()
        names = {c.name for c in existing.collections}
        if self._collection_name not in names:
            log.info("Creating collection '%s' (dim=%d)", self._collection_name, self._vector_size)
            await self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=self._vector_size, distance=Distance.COSINE),
            )
        else:
            log.info("Collection '%s' already exists", self._collection_name)

    async def upsert(self, points: list[PointStruct]) -> None:
        log.debug("Upserting %d points into '%s'", len(points), self._collection_name)
        await self._client.upsert(collection_name=self._collection_name, points=points)
        log.info("Upserted %d points into '%s'", len(points), self._collection_name)

    async def search(self, query_vector: list[float], top_k: int):
        log.debug("Searching '%s' top_k=%d", self._collection_name, top_k)
        response = await self._client.query_points(
            collection_name=self._collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )
        log.info("Search returned %d results", len(response.points))
        return response.points

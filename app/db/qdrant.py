from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams


class QdrantRepository:
    def __init__(self, client: AsyncQdrantClient, collection_name: str, vector_size: int):
        self._client = client
        self._collection_name = collection_name
        self._vector_size = vector_size

    async def ensure_collection(self) -> None:
        existing = await self._client.get_collections()
        names = {c.name for c in existing.collections}
        if self._collection_name not in names:
            await self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=self._vector_size, distance=Distance.COSINE),
            )

    async def upsert(self, points: list[PointStruct]) -> None:
        await self._client.upsert(collection_name=self._collection_name, points=points)

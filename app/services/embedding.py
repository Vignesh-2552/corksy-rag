import asyncio

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


async def embed_in_batches(
    chunks: list[Document],
    embeddings: Embeddings,
    batch_size: int = 100,
) -> list[list[float]]:
    texts = [chunk.page_content for chunk in chunks]
    results: list[list[float]] = []

    loop = asyncio.get_event_loop()
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch_vectors = await loop.run_in_executor(
            None, embeddings.embed_documents, batch
        )
        results.extend(batch_vectors)

    return results

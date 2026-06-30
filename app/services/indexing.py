import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile
from langchain_community.document_loaders import CSVLoader, JSONLoader, TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import PointStruct

from app.config import settings
from app.db.qdrant import QdrantRepository
from app.services.embedding import embed_in_batches


def _supported_extensions() -> set[str]:
    return {ext.strip() for ext in settings.supported_extensions.split(",")}


def get_loader(file_path: str, extension: str):
    match extension:
        case ".pdf":
            return PyPDFLoader(file_path)
        case ".txt":
            return TextLoader(file_path, encoding="utf-8")
        case ".md":
            return TextLoader(file_path, encoding="utf-8")
        case ".json":
            return JSONLoader(file_path, jq_schema=".", text_content=False)
        case ".csv":
            return CSVLoader(file_path)
        case _:
            raise ValueError(f"Unsupported extension: {extension}")


def _make_doc_id(source_file: str, chunk_index: int) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_file}:{chunk_index}"))


class IndexingService:
    def __init__(self, qdrant_repo: QdrantRepository, embeddings: Embeddings):
        self._qdrant = qdrant_repo
        self._embeddings = embeddings
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

    async def index_document(self, upload: UploadFile) -> dict:
        supported = _supported_extensions()
        max_bytes = settings.max_file_size_mb * 1024 * 1024

        ext = Path(upload.filename or "").suffix.lower()
        if ext not in supported:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Accepted: {', '.join(sorted(supported))}",
            )

        content = await upload.read()
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File '{upload.filename}' exceeds the {settings.max_file_size_mb} MB limit.",
            )

        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            loader = get_loader(tmp_path, ext)
            docs = loader.load()
        finally:
            os.unlink(tmp_path)

        source_file = upload.filename or "unknown"
        chunks = self._splitter.split_documents(docs)
        for i, chunk in enumerate(chunks):
            chunk.metadata["source_file"] = source_file
            chunk.metadata["chunk_index"] = i
            chunk.metadata["doc_id"] = _make_doc_id(source_file, i)
            chunk.metadata["indexed_at"] = datetime.now(timezone.utc).isoformat()

        if not chunks:
            return {"status": "indexed", "files": [source_file], "chunks": 0}

        try:
            vectors = await embed_in_batches(chunks, self._embeddings)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Embedding failed: {exc}") from exc

        points = [
            PointStruct(
                id=chunk.metadata["doc_id"],
                vector=vector,
                payload={
                    "doc_id": chunk.metadata["doc_id"],
                    "source_file": chunk.metadata["source_file"],
                    "chunk_index": chunk.metadata["chunk_index"],
                    "text": chunk.page_content,
                    "indexed_at": chunk.metadata["indexed_at"],
                },
            )
            for chunk, vector in zip(chunks, vectors)
        ]

        try:
            await self._qdrant.upsert(points)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"Qdrant upsert failed: {exc}") from exc

        return {"status": "indexed", "files": [source_file], "chunks": len(chunks)}

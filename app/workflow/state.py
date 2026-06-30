from typing import TypedDict

from langchain_core.documents import Document

from app.models.response import SourceReference


class RAGState(TypedDict):
    session_id: str
    question: str
    top_k: int
    retrieved_docs: list[Document]
    answer: str
    sources: list[SourceReference]

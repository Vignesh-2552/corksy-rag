from typing import Literal, TypedDict

from langchain_core.documents import Document

from app.schemas.response import SourceReference


class Intent(TypedDict):
    needs_documents: bool
    needs_query: bool
    reasoning: str


class PlanStep(TypedDict):
    tool: Literal["search_documents", "run_query"]
    query_name: str
    params: dict
    reasoning: str


class QueryResult(TypedDict):
    query_name: str
    params: dict
    result: str
    error: str | None


class RAGState(TypedDict):
    session_id: str
    question: str
    top_k: int
    intent: Intent
    plan: list[PlanStep]
    retrieved_docs: list[Document]
    query_results: list[QueryResult]
    answer: str
    sources: list[SourceReference]

from app.core.logger import get_logger
from app.schemas.response import SourceReference
from app.agents.state import RAGState

log = get_logger("corksy.agents.generate")


async def generate(state: RAGState, generation_service) -> RAGState:
    docs = state["retrieved_docs"]
    query_results = state["query_results"]
    log.info(
        "[generate] session=%s building answer from %d docs, %d query result(s)",
        state["session_id"],
        len(docs),
        len(query_results),
    )
    answer = await generation_service.generate(state["question"], docs, query_results)
    sources = [
        SourceReference(
            doc_id=doc.metadata.get("doc_id", ""),
            source_file=doc.metadata.get("source_file", ""),
            score=float(doc.metadata.get("score", 0.0)),
            snippet=doc.page_content[:200],
        )
        for doc in docs
    ]
    log.info("[generate] done — answer=%d chars sources=%d", len(answer), len(sources))
    return {**state, "answer": answer, "sources": sources}

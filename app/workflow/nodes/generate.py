from app.core.logger import get_logger
from app.schemas.response import SourceReference
from app.workflow.state import RAGState

log = get_logger("corksy.workflow.generate")

SYSTEM_PROMPT = (
    "You are a helpful e-commerce assistant. "
    "Answer the customer's question using ONLY the context provided below. "
    "If the answer is not in the context, say you don't know.\n\nContext:\n{context}"
)


async def generate(state: RAGState, generation_service) -> RAGState:
    docs = state["retrieved_docs"]
    log.info("[generate] session=%s building answer from %d docs", state["session_id"], len(docs))
    answer = await generation_service.generate(state["question"], docs)
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

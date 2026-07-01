from app.core.logger import get_logger
from app.agents.state import RAGState

log = get_logger("corksy.agents.retrieve")


async def retrieve(state: RAGState, retrieval_service) -> RAGState:
    log.info("[retrieve] session=%s question='%s'", state["session_id"], state["question"][:80])
    docs = await retrieval_service.search(state["question"], state["top_k"])
    log.info("[retrieve] found %d docs", len(docs))
    return {**state, "retrieved_docs": docs}

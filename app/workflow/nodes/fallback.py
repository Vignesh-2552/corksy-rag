from app.logger import get_logger
from app.workflow.state import RAGState

log = get_logger("corksy.workflow.fallback")

FALLBACK_MESSAGE = (
    "I couldn't find relevant information for your question. "
    "Please contact our support team for help."
)


async def fallback(state: RAGState) -> RAGState:
    log.warning("[fallback] session=%s no docs found — returning fallback message", state["session_id"])
    return {**state, "answer": FALLBACK_MESSAGE, "sources": []}

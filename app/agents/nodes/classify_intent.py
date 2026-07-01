from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.agents.prompts.classify_intent import SYSTEM_PROMPT
from app.agents.state import RAGState
from app.core.logger import get_logger

log = get_logger("corksy.agents.classify_intent")


class _IntentSchema(BaseModel):
    needs_documents: bool = Field(description="Whether the knowledge base must be searched")
    needs_query: bool = Field(description="Whether a live data lookup must be run")
    reasoning: str = Field(description="One-sentence explanation of the decision")


async def classify_intent(state: RAGState, llm: BaseChatModel) -> RAGState:
    log.info("[classify_intent] session=%s question='%s'", state["session_id"], state["question"][:80])
    result: _IntentSchema = await llm.with_structured_output(_IntentSchema).ainvoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=state["question"])]
    )
    log.info(
        "[classify_intent] session=%s needs_documents=%s needs_query=%s",
        state["session_id"],
        result.needs_documents,
        result.needs_query,
    )
    intent = {
        "needs_documents": result.needs_documents,
        "needs_query": result.needs_query,
        "reasoning": result.reasoning,
    }
    return {**state, "intent": intent}

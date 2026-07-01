from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.agents.prompts.plan import SYSTEM_PROMPT
from app.agents.state import RAGState
from app.core.logger import get_logger

log = get_logger("corksy.agents.plan")


class _PlanStepSchema(BaseModel):
    tool: str = Field(description="'search_documents' or 'run_query'")
    query_name: str = Field(default="", description="Template name, required when tool is run_query")
    params: dict = Field(default_factory=dict, description="Params for the query template")
    reasoning: str = Field(description="Why this step is needed")


class _PlanSchema(BaseModel):
    steps: list[_PlanStepSchema]


async def plan(state: RAGState, llm: BaseChatModel, available_queries: list[str]) -> RAGState:
    log.info("[plan] session=%s intent=%s", state["session_id"], state["intent"])
    prompt = SYSTEM_PROMPT.format(
        available_queries="\n".join(f"- {q}" for q in available_queries) or "(none configured)"
    )
    intent = state["intent"]
    result: _PlanSchema = await llm.with_structured_output(_PlanSchema).ainvoke(
        [
            SystemMessage(content=prompt),
            HumanMessage(
                content=(
                    f"Question: {state['question']}\n"
                    f"needs_documents={intent['needs_documents']} needs_query={intent['needs_query']}"
                )
            ),
        ]
    )
    steps = [
        {"tool": s.tool, "query_name": s.query_name, "params": s.params, "reasoning": s.reasoning}
        for s in result.steps
    ]
    log.info("[plan] session=%s built %d step(s): %s", state["session_id"], len(steps), [s["tool"] for s in steps])
    return {**state, "plan": steps}

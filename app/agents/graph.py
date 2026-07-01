from functools import partial

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph

from app.services.generation import GenerationService
from app.services.query_tool import QueryToolService
from app.services.retrieval import RetrievalService
from app.agents.nodes.classify_intent import classify_intent
from app.agents.nodes.execute_plan import execute_plan
from app.agents.nodes.fallback import fallback
from app.agents.nodes.generate import generate
from app.agents.nodes.plan import plan
from app.agents.state import RAGState


def _route_after_intent(state: RAGState) -> str:
    intent = state["intent"]
    return "plan" if (intent["needs_documents"] or intent["needs_query"]) else "fallback"


def build_rag_graph(
    retrieval_service: RetrievalService,
    generation_service: GenerationService,
    query_tool_service: QueryToolService,
    llm: BaseChatModel,
    available_queries: list[str] | None = None,
):
    graph = StateGraph(RAGState)

    graph.add_node("classify_intent", partial(classify_intent, llm=llm))
    graph.add_node("plan", partial(plan, llm=llm, available_queries=available_queries or []))
    graph.add_node(
        "execute_plan",
        partial(execute_plan, retrieval_service=retrieval_service, query_tool_service=query_tool_service),
    )
    graph.add_node("generate", partial(generate, generation_service=generation_service))
    graph.add_node("fallback", fallback)

    graph.add_edge(START, "classify_intent")
    graph.add_conditional_edges("classify_intent", _route_after_intent, {"plan": "plan", "fallback": "fallback"})
    graph.add_edge("plan", "execute_plan")
    graph.add_edge("execute_plan", "generate")
    graph.add_edge("generate", END)
    graph.add_edge("fallback", END)

    return graph.compile()

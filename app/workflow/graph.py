from functools import partial

from langgraph.graph import END, START, StateGraph

from app.services.generation import GenerationService
from app.services.retrieval import RetrievalService
from app.workflow.nodes.fallback import fallback
from app.workflow.nodes.generate import generate
from app.workflow.nodes.retrieve import retrieve
from app.workflow.state import RAGState


def _has_docs(state: RAGState) -> str:
    return "generate" if state["retrieved_docs"] else "fallback"


def build_rag_graph(retrieval_service: RetrievalService, generation_service: GenerationService):
    graph = StateGraph(RAGState)

    graph.add_node("retrieve", partial(retrieve, retrieval_service=retrieval_service))
    graph.add_node("generate", partial(generate, generation_service=generation_service))
    graph.add_node("fallback", fallback)

    graph.add_edge(START, "retrieve")
    graph.add_conditional_edges("retrieve", _has_docs, {"generate": "generate", "fallback": "fallback"})
    graph.add_edge("generate", END)
    graph.add_edge("fallback", END)

    return graph.compile()

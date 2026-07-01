from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.containers import Container
from app.schemas.request import AskRequest
from app.schemas.response import AskResponse
from app.services.generation import GenerationService
from app.services.retrieval import RetrievalService
from app.workflow.graph import build_rag_graph
from app.workflow.state import RAGState

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
@inject
async def ask(
    body: AskRequest,
    retrieval_service: RetrievalService = Depends(Provide[Container.retrieval_service]),
    generation_service: GenerationService = Depends(Provide[Container.generation_service]),
) -> AskResponse:
    rag_app = build_rag_graph(retrieval_service, generation_service)
    initial: RAGState = {
        "session_id": body.session_id,
        "question": body.question,
        "top_k": body.top_k,
        "retrieved_docs": [],
        "answer": "",
        "sources": [],
    }
    result: RAGState = await rag_app.ainvoke(initial)
    return AskResponse(
        answer=result["answer"],
        sources=result["sources"],
        session_id=result["session_id"],
    )


@router.post("/ask/stream")
@inject
async def ask_stream(
    body: AskRequest,
    retrieval_service: RetrievalService = Depends(Provide[Container.retrieval_service]),
    generation_service: GenerationService = Depends(Provide[Container.generation_service]),
) -> StreamingResponse:
    async def event_stream():
        docs = await retrieval_service.search(body.question, body.top_k)
        if not docs:
            from app.workflow.nodes.fallback import FALLBACK_MESSAGE
            yield f"data: {FALLBACK_MESSAGE}\n\n"
        else:
            async for token in generation_service.astream(body.question, docs):
                if token:
                    yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

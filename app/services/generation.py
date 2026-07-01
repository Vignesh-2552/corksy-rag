from typing import AsyncIterator

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.prompts.generate import SYSTEM_PROMPT
from app.core.logger import get_logger

log = get_logger("corksy.generation")


class GenerationService:
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    def _build_context(self, docs: list[Document], query_results: list[dict]) -> str:
        parts = [doc.page_content for doc in docs]
        parts += [
            f"Result of '{r['query_name']}': {r['result']}" for r in query_results if not r.get("error")
        ]
        return "\n\n".join(parts)

    def _messages(self, question: str, docs: list[Document], query_results: list[dict]) -> list:
        context = self._build_context(docs, query_results)
        return [
            SystemMessage(content=SYSTEM_PROMPT.format(context=context)),
            HumanMessage(content=question),
        ]

    async def generate(self, question: str, docs: list[Document], query_results: list[dict] | None = None) -> str:
        query_results = query_results or []
        log.info(
            "Generating answer for question: '%s' with %d docs, %d query result(s)",
            question[:80],
            len(docs),
            len(query_results),
        )
        response = await self._llm.ainvoke(self._messages(question, docs, query_results))
        log.info("Answer generated (%d chars)", len(response.content))
        return response.content

    async def astream(
        self, question: str, docs: list[Document], query_results: list[dict] | None = None
    ) -> AsyncIterator[str]:
        async for chunk in self._llm.astream(self._messages(question, docs, query_results or [])):
            yield chunk.content

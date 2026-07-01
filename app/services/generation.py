from typing import AsyncIterator

from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.logger import get_logger

log = get_logger("corksy.generation")

SYSTEM_PROMPT = (
    "You are a helpful e-commerce assistant. "
    "Answer the customer's question using ONLY the context provided below. "
    "If the answer is not in the context, say you don't know.\n\nContext:\n{context}"
)


class GenerationService:
    def __init__(self, llm: BaseChatModel):
        self._llm = llm

    def _messages(self, question: str, docs: list[Document]) -> list:
        context = "\n\n".join(doc.page_content for doc in docs)
        return [
            SystemMessage(content=SYSTEM_PROMPT.format(context=context)),
            HumanMessage(content=question),
        ]

    async def generate(self, question: str, docs: list[Document]) -> str:
        log.info("Generating answer for question: '%s' with %d docs", question[:80], len(docs))
        response = await self._llm.ainvoke(self._messages(question, docs))
        log.info("Answer generated (%d chars)", len(response.content))
        return response.content

    async def astream(self, question: str, docs: list[Document]) -> AsyncIterator[str]:
        async for chunk in self._llm.astream(self._messages(question, docs)):
            yield chunk.content

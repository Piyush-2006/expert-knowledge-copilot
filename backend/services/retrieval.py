from __future__ import annotations

import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.core.config import Settings, get_settings
from src.ingestion.schemas import SearchResult

logger = logging.getLogger(__name__)

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an industrial knowledge copilot. Answer using only the provided context. "
            "If the context is insufficient, say you do not have enough information.",
        ),
        (
            "human",
            "Question:\n{question}\n\nContext:\n{context}\n\nAnswer:",
        ),
    ]
)


def _build_context(matches: list[SearchResult]) -> str:
    if not matches:
        return "No relevant context found."

    sections: list[str] = []
    for match in matches:
        sections.append(
            f"[{match.filename} | page {match.page_number} | score {match.score:.4f}]\n"
            f"{match.content}"
        )
    return "\n\n".join(sections)


def generate_answer(question: str, matches: list[SearchResult], *, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required to generate answers.")

    llm = ChatOpenAI(
        model=settings.chat_model,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )
    chain = ANSWER_PROMPT | llm
    context = _build_context(matches)

    logger.info("Generating answer for query: %s", question[:120])
    response = chain.invoke({"question": question, "context": context})
    content = response.content
    if isinstance(content, str):
        return content
    return str(content)

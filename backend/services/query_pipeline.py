from __future__ import annotations

import logging
from dataclasses import dataclass

from backend.schemas import Citation, RetrievedChunk
from backend.services.confidence import compute_confidence_score
from backend.services.retrieval import generate_answer
from src.core.config import Settings, get_settings
from src.ingestion.schemas import SearchResult
from src.ingestion.vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 4


@dataclass(frozen=True)
class QueryPipelineResult:
    query: str
    answer: str
    confidence_score: float
    citations: list[Citation]
    chunks: list[RetrievedChunk]


def _build_citations(matches: list[SearchResult]) -> list[Citation]:
    seen: set[tuple[str, int]] = set()
    citations: list[Citation] = []

    for match in matches:
        key = (match.filename, match.page_number)
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            Citation(
                document_name=match.filename,
                page_number=match.page_number,
            )
        )

    return citations


def _build_chunks(matches: list[SearchResult]) -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            chunk_id=match.chunk_id,
            content=match.content,
            document_name=match.filename,
            page_number=match.page_number,
            relevance_score=match.score,
        )
        for match in matches
    ]


def run_query_pipeline(
    query: str,
    *,
    vector_store: ChromaVectorStore,
    settings: Settings | None = None,
    top_k: int = DEFAULT_TOP_K,
) -> QueryPipelineResult:
    settings = settings or get_settings()
    top_k = min(max(top_k, 1), DEFAULT_TOP_K)

    logger.info("Running query pipeline for: %s", query[:120])
    matches = vector_store.similarity_search(query, top_k=top_k)
    confidence_score = compute_confidence_score(matches)
    citations = _build_citations(matches)
    chunks = _build_chunks(matches)

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required to generate answers.")

    answer = generate_answer(query, matches, settings=settings)

    logger.info(
        "Query pipeline complete: %s chunks, confidence %.1f",
        len(chunks),
        confidence_score,
    )

    return QueryPipelineResult(
        query=query,
        answer=answer,
        confidence_score=confidence_score,
        citations=citations,
        chunks=chunks,
    )

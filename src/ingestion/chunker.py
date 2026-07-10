from __future__ import annotations

import uuid

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import Settings, get_settings
from src.ingestion.schemas import PageContent, TextChunk


def chunk_pages(
    pages: list[PageContent],
    filename: str,
    *,
    settings: Settings | None = None,
) -> list[TextChunk]:
    """Split page text into chunks while preserving filename and page metadata."""
    settings = settings or get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    documents = [
        Document(
            page_content=page.text,
            metadata={
                "filename": filename,
                "page_number": page.page_number,
            },
        )
        for page in pages
        if page.text.strip()
    ]

    if not documents:
        return []

    split_docs = splitter.split_documents(documents)
    chunks: list[TextChunk] = []

    for doc in split_docs:
        page_number = int(doc.metadata["page_number"])
        chunk_id = f"{filename}_p{page_number}_{uuid.uuid4().hex[:8]}"
        chunks.append(
            TextChunk(
                chunk_id=chunk_id,
                content=doc.page_content,
                filename=filename,
                page_number=page_number,
            )
        )

    return chunks

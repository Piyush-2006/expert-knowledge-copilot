from __future__ import annotations

import logging
from pathlib import Path

from src.core.config import Settings, get_settings
from src.ingestion.chunker import chunk_pages
from src.ingestion.pdf_reader import extract_text_from_pdf
from src.ingestion.schemas import IngestionResult
from src.ingestion.vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)


class PDFIngestionPipeline:
    """End-to-end PDF ingestion: read, chunk, embed, and store."""

    def __init__(
        self,
        vector_store: ChromaVectorStore | None = None,
        *,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._vector_store = vector_store or ChromaVectorStore(settings=self._settings)

    def ingest(self, pdf_path: str | Path) -> IngestionResult:
        pdf_path = Path(pdf_path)
        filename = pdf_path.name

        logger.info("Starting ingestion for %s", filename)
        pages = extract_text_from_pdf(pdf_path, settings=self._settings)
        chunks = chunk_pages(pages, filename, settings=self._settings)
        chunk_ids = self._vector_store.add_chunks(chunks)

        result = IngestionResult(
            filename=filename,
            page_count=len(pages),
            chunk_count=len(chunk_ids),
            ocr_page_count=sum(1 for page in pages if page.used_ocr),
        )
        logger.info(
            "Ingested %s: %s pages, %s chunks (%s OCR pages)",
            result.filename,
            result.page_count,
            result.chunk_count,
            result.ocr_page_count,
        )
        return result

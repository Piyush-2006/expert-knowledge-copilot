"""CLI entrypoint for ingesting a PDF into ChromaDB."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.ingestion import PDFIngestionPipeline

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest a PDF into ChromaDB")
    parser.add_argument("pdf_path", type=Path, help="Path to the PDF file")
    args = parser.parse_args(argv)

    try:
        result = PDFIngestionPipeline().ingest(args.pdf_path)
    except (FileNotFoundError, ValueError) as exc:
        logger.error("%s", exc)
        return 1

    print(
        f"Ingested '{result.filename}': "
        f"{result.page_count} pages, "
        f"{result.chunk_count} chunks, "
        f"{result.ocr_page_count} OCR pages"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import logging
from pathlib import Path

import pytesseract
from pypdf import PdfReader
from pdf2image import convert_from_path

from src.core.config import Settings, get_settings
from src.ingestion.schemas import PageContent

logger = logging.getLogger(__name__)


def _configure_tesseract(settings: Settings) -> None:
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


def _extract_page_with_pypdf(reader: PdfReader, page_index: int) -> str:
    page = reader.pages[page_index]
    text = page.extract_text() or ""
    return text.strip()


def _extract_page_with_ocr(pdf_path: Path, page_number: int) -> str:
    images = convert_from_path(
        str(pdf_path),
        first_page=page_number,
        last_page=page_number,
    )
    if not images:
        return ""

    text = pytesseract.image_to_string(images[0])
    return text.strip()


def extract_text_from_pdf(
    pdf_path: Path,
    *,
    settings: Settings | None = None,
) -> list[PageContent]:
    """Extract text from each PDF page, falling back to OCR when needed."""
    settings = settings or get_settings()
    _configure_tesseract(settings)

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {pdf_path.name}")

    reader = PdfReader(str(pdf_path))
    pages: list[PageContent] = []

    for page_index in range(len(reader.pages)):
        page_number = page_index + 1
        text = _extract_page_with_pypdf(reader, page_index)
        used_ocr = False

        if len(text) < settings.ocr_min_text_length:
            logger.info(
                "Low text on page %s of %s; using OCR fallback",
                page_number,
                pdf_path.name,
            )
            ocr_text = _extract_page_with_ocr(pdf_path, page_number)
            if len(ocr_text) >= len(text):
                text = ocr_text
                used_ocr = True

        pages.append(
            PageContent(
                page_number=page_number,
                text=text,
                used_ocr=used_ocr,
            )
        )

    return pages

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from src.ingestion import PDFIngestionPipeline
from src.schemas.ingestion import IngestionResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/pdf", response_model=IngestionResponse, status_code=status.HTTP_201_CREATED)
async def ingest_pdf(file: UploadFile = File(...)) -> IngestionResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    suffix = Path(file.filename).suffix or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        result = PDFIngestionPipeline().ingest(tmp_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("PDF ingestion failed for %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF ingestion failed.",
        ) from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    return IngestionResponse(
        filename=result.filename,
        page_count=result.page_count,
        chunk_count=result.chunk_count,
        ocr_page_count=result.ocr_page_count,
    )

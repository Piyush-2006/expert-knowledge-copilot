from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.dependencies import get_ingestion_pipeline
from backend.schemas import UploadResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["upload"])


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        logger.warning("Rejected upload with invalid file type: %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    suffix = Path(file.filename).suffix or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        logger.info("Upload received: %s", file.filename)
        result = get_ingestion_pipeline().ingest(tmp_path)
    except FileNotFoundError as exc:
        logger.error("Upload failed, file not found: %s", exc)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        logger.error("Upload failed validation: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected upload failure for %s", file.filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest PDF.",
        ) from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    return UploadResponse(
        filename=result.filename,
        page_count=result.page_count,
        chunk_count=result.chunk_count,
        ocr_page_count=result.ocr_page_count,
        document_id=result.filename,
    )

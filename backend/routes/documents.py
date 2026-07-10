from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import get_vector_store
from backend.schemas import DeleteDocumentResponse, DocumentInfo, DocumentsResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["documents"])


@router.get("/documents", response_model=DocumentsResponse)
def list_documents() -> DocumentsResponse:
    try:
        records = get_vector_store().list_documents()
    except Exception as exc:
        logger.exception("Failed to list documents")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents.",
        ) from exc

    documents = [
        DocumentInfo(
            id=record.id,
            filename=record.filename,
            chunk_count=record.chunk_count,
            page_numbers=record.page_numbers,
        )
        for record in records
    ]
    return DocumentsResponse(documents=documents, total=len(documents))


@router.delete("/document/{document_id}", response_model=DeleteDocumentResponse)
def delete_document(document_id: str) -> DeleteDocumentResponse:
    try:
        deleted_chunks = get_vector_store().delete_document(document_id)
    except Exception as exc:
        logger.exception("Failed to delete document %s", document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document.",
        ) from exc

    if deleted_chunks == 0:
        logger.warning("Document not found for deletion: %s", document_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    logger.info("Deleted document %s (%s chunks)", document_id, deleted_chunks)
    return DeleteDocumentResponse(document_id=document_id, deleted_chunks=deleted_chunks)

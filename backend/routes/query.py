from __future__ import annotations

import logging
import time

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import get_vector_store
from backend.schemas import QueryRequest, QueryResponse
from backend.services.query_pipeline import run_query_pipeline
from src.core.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query_knowledge(
    payload: QueryRequest,
) -> QueryResponse:

    settings = get_settings()

    start_time = time.time()

    try:
        result = run_query_pipeline(
            payload.query,
            vector_store=get_vector_store(),
            settings=settings,
        )

        ###################################################
        # Confidence Label
        ###################################################

        score = result.confidence_score

        if score >= 0.80:
            confidence_label = "High"
        elif score >= 0.60:
            confidence_label = "Medium"
        else:
            confidence_label = "Low"

        processing_time = round(
            time.time() - start_time,
            2,
        )

        logger.info(
            "Query completed in %ss",
            processing_time,
        )

        return QueryResponse(
            query=result.query,
            answer=result.answer,
            confidence_score=score,
            confidence_level=confidence_label,
            citations=result.citations,
            chunks=result.chunks,
            processing_time=processing_time,
        )

    except ValueError as exc:

        logger.warning(
            "Query validation failed: %s",
            exc,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Query pipeline failed"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Knowledge query failed.",
        ) from exc
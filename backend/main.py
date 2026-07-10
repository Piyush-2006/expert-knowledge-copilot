from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from backend.routes import documents, health, query, upload
from backend.schemas import ErrorResponse
from src.core.config import get_settings

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    logger.info(
        "Starting %s (%s)",
        settings.app_name,
        settings.app_env,
    )

    yield

    logger.info(
        "Shutting down %s",
        settings.app_name,
    )


def create_app() -> FastAPI:
    configure_logging()

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Industrial Expert Knowledge Copilot API",
        lifespan=lifespan,
    )

    ##########################################################
    # Middleware
    ##########################################################

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()

        response = await call_next(request)

        process_time = round(time.time() - start, 2)

        logger.info(
            "%s %s completed in %ss",
            request.method,
            request.url.path,
            process_time,
        )

        response.headers["X-Process-Time"] = str(process_time)

        return response

    ##########################################################
    # Exception Handlers
    ##########################################################

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _: Request,
        exc: HTTPException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                detail=str(exc.detail)
            ).model_dump(),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(
        _: Request,
        exc: ValueError,
    ):
        logger.warning(exc)

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                detail=str(exc)
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        _: Request,
        exc: Exception,
    ):
        logger.exception(exc)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                detail="Internal server error"
            ).model_dump(),
        )

    ##########################################################
    # Routers
    ##########################################################

    app.include_router(health.router)
    app.include_router(upload.router)
    app.include_router(query.router)
    app.include_router(documents.router)

    ##########################################################
    # Root Endpoint
    ##########################################################

    @app.get("/")
    async def root():
        return {
            "app": settings.app_name,
            "version": "0.1.0",
            "status": "running",
            "docs": "/docs",
        }

    return app


app = create_app()
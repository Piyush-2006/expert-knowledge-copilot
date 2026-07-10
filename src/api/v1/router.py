from fastapi import APIRouter

from src.api.v1 import ingestion

api_router = APIRouter()
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])

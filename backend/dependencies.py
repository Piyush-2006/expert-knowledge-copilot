from functools import lru_cache

from src.core.config import get_settings
from src.ingestion import ChromaVectorStore, PDFIngestionPipeline


@lru_cache
def get_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore(settings=get_settings())


@lru_cache
def get_ingestion_pipeline() -> PDFIngestionPipeline:
    return PDFIngestionPipeline(vector_store=get_vector_store(), settings=get_settings())

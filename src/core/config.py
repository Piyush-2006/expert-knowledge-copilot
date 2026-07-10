from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Expert Knowledge Copilot"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"
    retrieval_top_k: int = 4

    chroma_persist_dir: str = "data/vector_index"
    chroma_collection_name: str = "knowledge_chunks"

    chunk_size: int = 1000
    chunk_overlap: int = 200
    ocr_min_text_length: int = 50
    tesseract_cmd: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()

from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from src.core.config import Settings, get_settings
from src.ingestion.schemas import DocumentRecord, SearchResult, TextChunk


class ChromaVectorStore:
    """Persist chunk embeddings and metadata in ChromaDB."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        persist_directory: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        settings = settings or get_settings()
        self._settings = settings
        self._persist_directory = persist_directory or settings.chroma_persist_dir
        self._collection_name = collection_name or settings.chroma_collection_name

        Path(self._persist_directory).mkdir(parents=True, exist_ok=True)

        self._embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key or None,
        )
        self._store = Chroma(
            collection_name=self._collection_name,
            embedding_function=self._embeddings,
            persist_directory=self._persist_directory,
        )

    def add_chunks(self, chunks: list[TextChunk]) -> list[str]:
        if not chunks:
            return []

        documents = [
            Document(
                page_content=chunk.content,
                metadata={
                    "filename": chunk.filename,
                    "page_number": chunk.page_number,
                    "chunk_id": chunk.chunk_id,
                },
            )
            for chunk in chunks
        ]

        ids = [chunk.chunk_id for chunk in chunks]
        self._store.add_documents(documents=documents, ids=ids)
        return ids

    def similarity_search(self, query: str, *, top_k: int | None = None) -> list[SearchResult]:
        top_k = top_k or self._settings.retrieval_top_k
        results = self._store.similarity_search_with_score(query, k=top_k)

        matches: list[SearchResult] = []
        for document, score in results:
            metadata = document.metadata
            matches.append(
                SearchResult(
                    chunk_id=str(metadata.get("chunk_id", "")),
                    content=document.page_content,
                    filename=str(metadata.get("filename", "")),
                    page_number=int(metadata.get("page_number", 0)),
                    score=float(score),
                )
            )
        return matches

    def list_documents(self) -> list[DocumentRecord]:
        collection = self._store._collection
        records = collection.get(include=["metadatas"])

        grouped: dict[str, dict[str, set[int] | int]] = {}
        for metadata in records.get("metadatas", []):
            if not metadata:
                continue

            filename = str(metadata.get("filename", ""))
            if not filename:
                continue

            if filename not in grouped:
                grouped[filename] = {"chunk_count": 0, "page_numbers": set()}

            grouped[filename]["chunk_count"] = int(grouped[filename]["chunk_count"]) + 1
            page_numbers = grouped[filename]["page_numbers"]
            assert isinstance(page_numbers, set)
            page_numbers.add(int(metadata.get("page_number", 0)))

        documents = [
            DocumentRecord(
                id=filename,
                filename=filename,
                chunk_count=int(data["chunk_count"]),
                page_numbers=sorted(int(page) for page in data["page_numbers"]),  # type: ignore[arg-type]
            )
            for filename, data in sorted(grouped.items())
        ]
        return documents

    def delete_document(self, document_id: str) -> int:
        collection = self._store._collection
        existing = collection.get(where={"filename": document_id}, include=[])

        ids = existing.get("ids", [])
        if not ids:
            return 0

        collection.delete(ids=ids)
        return len(ids)

    @property
    def collection_name(self) -> str:
        return self._collection_name

    @property
    def persist_directory(self) -> str:
        return self._persist_directory

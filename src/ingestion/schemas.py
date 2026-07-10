from dataclasses import dataclass


@dataclass(frozen=True)
class PageContent:
    page_number: int
    text: str
    used_ocr: bool = False


@dataclass(frozen=True)
class TextChunk:
    chunk_id: str
    content: str
    filename: str
    page_number: int


@dataclass(frozen=True)
class IngestionResult:
    filename: str
    page_count: int
    chunk_count: int
    ocr_page_count: int


@dataclass(frozen=True)
class SearchResult:
    chunk_id: str
    content: str
    filename: str
    page_number: int
    score: float


@dataclass(frozen=True)
class DocumentRecord:
    id: str
    filename: str
    chunk_count: int
    page_numbers: list[int]

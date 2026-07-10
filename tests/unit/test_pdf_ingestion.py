import pytest
from langchain_core.documents import Document

from src.ingestion.chunker import chunk_pages
from src.ingestion.pdf_reader import extract_text_from_pdf
from src.ingestion.pipeline import PDFIngestionPipeline
from src.ingestion.schemas import PageContent, TextChunk
from src.core.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        chunk_size=100,
        chunk_overlap=20,
        ocr_min_text_length=10,
        openai_api_key="test-key",
    )


def test_chunk_pages_assigns_metadata(settings: Settings) -> None:
    pages = [
        PageContent(page_number=1, text="A" * 250),
        PageContent(page_number=2, text="Short page"),
    ]

    chunks = chunk_pages(pages, "manual.pdf", settings=settings)

    assert len(chunks) >= 2
    assert all(chunk.filename == "manual.pdf" for chunk in chunks)
    assert all(chunk.chunk_id.startswith("manual.pdf_p") for chunk in chunks)
    assert {chunk.page_number for chunk in chunks} == {1, 2}


def test_chunk_pages_skips_empty_pages(settings: Settings) -> None:
    pages = [
        PageContent(page_number=1, text="   "),
        PageContent(page_number=2, text="Valid content for chunking."),
    ]

    chunks = chunk_pages(pages, "empty.pdf", settings=settings)

    assert len(chunks) == 1
    assert chunks[0].page_number == 2


def test_extract_text_from_pdf_uses_ocr_fallback(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    tmp_path,
) -> None:
    pdf_path = tmp_path / "scan.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    class FakePage:
        def extract_text(self) -> str:
            return ""

    class FakeReader:
        pages = [FakePage(), FakePage()]

    monkeypatch.setattr("src.ingestion.pdf_reader.PdfReader", lambda _: FakeReader())
    monkeypatch.setattr(
        "src.ingestion.pdf_reader.convert_from_path",
        lambda *_args, **_kwargs: [object(), object()],
    )
    monkeypatch.setattr(
        "src.ingestion.pdf_reader.pytesseract.image_to_string",
        lambda _image: "OCR extracted text content",
    )

    pages = extract_text_from_pdf(pdf_path, settings=settings)

    assert len(pages) == 2
    assert all(page.used_ocr for page in pages)
    assert pages[0].page_number == 1
    assert "OCR extracted" in pages[0].text


def test_pipeline_ingest_orchestrates_steps(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
    tmp_path,
) -> None:
    pdf_path = tmp_path / "report.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    pages = [PageContent(page_number=1, text="Pipeline test content.")]
    chunks = [
        TextChunk(
            chunk_id="report.pdf_p1_abc12345",
            content="Pipeline test content.",
            filename="report.pdf",
            page_number=1,
        )
    ]
    stored_ids: list[str] = []

    monkeypatch.setattr(
        "src.ingestion.pipeline.extract_text_from_pdf",
        lambda *_args, **_kwargs: pages,
    )
    monkeypatch.setattr(
        "src.ingestion.pipeline.chunk_pages",
        lambda *_args, **_kwargs: chunks,
    )

    class FakeVectorStore:
        def add_chunks(self, received_chunks: list[TextChunk]) -> list[str]:
            stored_ids.extend(chunk.chunk_id for chunk in received_chunks)
            return stored_ids

    result = PDFIngestionPipeline(
        vector_store=FakeVectorStore(),  # type: ignore[arg-type]
        settings=settings,
    ).ingest(pdf_path)

    assert result.filename == "report.pdf"
    assert result.page_count == 1
    assert result.chunk_count == 1
    assert stored_ids == ["report.pdf_p1_abc12345"]


def test_vector_store_add_chunks_builds_documents(
    monkeypatch: pytest.MonkeyPatch,
    settings: Settings,
) -> None:
    captured: dict[str, list] = {"documents": [], "ids": []}

    class FakeChroma:
        def add_documents(self, documents: list[Document], ids: list[str]) -> None:
            captured["documents"] = documents
            captured["ids"] = ids

    monkeypatch.setattr("src.ingestion.vector_store.Chroma", lambda **_kwargs: FakeChroma())
    monkeypatch.setattr(
        "src.ingestion.vector_store.OpenAIEmbeddings",
        lambda **_kwargs: object(),
    )

    from src.ingestion.vector_store import ChromaVectorStore

    store = ChromaVectorStore(settings=settings, persist_directory="tmp-test-chroma")
    chunks = [
        TextChunk(
            chunk_id="doc.pdf_p3_deadbeef",
            content="Stored chunk text",
            filename="doc.pdf",
            page_number=3,
        )
    ]

    ids = store.add_chunks(chunks)

    assert ids == ["doc.pdf_p3_deadbeef"]
    assert captured["ids"] == ["doc.pdf_p3_deadbeef"]
    assert captured["documents"][0].page_content == "Stored chunk text"
    assert captured["documents"][0].metadata == {
        "filename": "doc.pdf",
        "page_number": 3,
        "chunk_id": "doc.pdf_p3_deadbeef",
    }

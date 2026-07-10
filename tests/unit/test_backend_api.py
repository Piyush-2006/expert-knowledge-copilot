import pytest
from fastapi.testclient import TestClient

from backend.dependencies import get_ingestion_pipeline, get_vector_store
from backend.main import app
from backend.services.query_pipeline import QueryPipelineResult
from backend.schemas import Citation, RetrievedChunk
from src.ingestion.schemas import DocumentRecord, IngestionResult


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_dependency_cache() -> None:
    get_vector_store.cache_clear()
    get_ingestion_pipeline.cache_clear()
    yield
    get_vector_store.cache_clear()
    get_ingestion_pipeline.cache_clear()


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "Expert Knowledge Copilot"


def test_upload_rejects_non_pdf(client: TestClient) -> None:
    response = client.post(
        "/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are supported."


def test_upload_ingests_pdf(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    expected = IngestionResult(
        filename="manual.pdf",
        page_count=2,
        chunk_count=4,
        ocr_page_count=1,
    )

    class FakePipeline:
        def ingest(self, _pdf_path) -> IngestionResult:
            return expected

    monkeypatch.setattr("backend.routes.upload.get_ingestion_pipeline", lambda: FakePipeline())

    response = client.post(
        "/upload",
        files={"file": ("manual.pdf", b"%PDF-1.4", "application/pdf")},
    )

    assert response.status_code == 201
    assert response.json() == {
        "filename": "manual.pdf",
        "page_count": 2,
        "chunk_count": 4,
        "ocr_page_count": 1,
        "document_id": "manual.pdf",
    }


def test_query_returns_json_pipeline_response(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline_result = QueryPipelineResult(
        query="How do I maintain the pump?",
        answer="Check the pump seal weekly.",
        confidence_score=89.3,
        citations=[
            Citation(document_name="manual.pdf", page_number=1),
        ],
        chunks=[
            RetrievedChunk(
                chunk_id="manual.pdf_p1_abcd1234",
                content="Pump maintenance steps",
                document_name="manual.pdf",
                page_number=1,
                relevance_score=0.12,
            )
        ],
    )

    monkeypatch.setattr(
        "backend.routes.query.run_query_pipeline",
        lambda *_args, **_kwargs: pipeline_result,
    )

    response = client.post(
        "/query",
        json={"query": "How do I maintain the pump?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "query": "How do I maintain the pump?",
        "answer": "Check the pump seal weekly.",
        "confidence_score": 89.3,
        "citations": [{"document_name": "manual.pdf", "page_number": 1}],
        "chunks": [
            {
                "chunk_id": "manual.pdf_p1_abcd1234",
                "content": "Pump maintenance steps",
                "document_name": "manual.pdf",
                "page_number": 1,
                "relevance_score": 0.12,
            }
        ],
    }


def test_list_documents(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    records = [
        DocumentRecord(
            id="manual.pdf",
            filename="manual.pdf",
            chunk_count=2,
            page_numbers=[1, 2],
        )
    ]

    class FakeVectorStore:
        def list_documents(self) -> list[DocumentRecord]:
            return records

    monkeypatch.setattr("backend.routes.documents.get_vector_store", lambda: FakeVectorStore())

    response = client.get("/documents")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["documents"][0]["filename"] == "manual.pdf"


def test_delete_document(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeVectorStore:
        def delete_document(self, document_id: str) -> int:
            assert document_id == "manual.pdf"
            return 3

    monkeypatch.setattr("backend.routes.documents.get_vector_store", lambda: FakeVectorStore())

    response = client.delete("/document/manual.pdf")
    assert response.status_code == 200
    assert response.json() == {"document_id": "manual.pdf", "deleted_chunks": 3}


def test_delete_document_not_found(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeVectorStore:
        def delete_document(self, _document_id: str) -> int:
            return 0

    monkeypatch.setattr("backend.routes.documents.get_vector_store", lambda: FakeVectorStore())

    response = client.delete("/document/missing.pdf")
    assert response.status_code == 404

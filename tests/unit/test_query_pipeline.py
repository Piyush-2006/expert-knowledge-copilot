import pytest

from backend.services.confidence import compute_confidence_score
from backend.services.query_pipeline import QueryPipelineResult, run_query_pipeline
from src.core.config import Settings
from src.ingestion.schemas import SearchResult


def test_compute_confidence_score() -> None:
    matches = [
        SearchResult("c1", "text", "manual.pdf", 1, 0.25),
        SearchResult("c2", "text", "manual.pdf", 2, 0.75),
    ]
    assert compute_confidence_score(matches) == 80.0
    assert compute_confidence_score([]) == 0.0


def test_run_query_pipeline_returns_json_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    matches = [
        SearchResult("manual.pdf_p1_abcd1234", "Pump maintenance steps", "manual.pdf", 1, 0.12),
        SearchResult("manual.pdf_p2_abcd5678", "Seal inspection checklist", "manual.pdf", 2, 0.18),
    ]

    class FakeVectorStore:
        def similarity_search(self, _query: str, *, top_k: int) -> list[SearchResult]:
            assert top_k == 4
            return matches

    monkeypatch.setattr(
        "backend.services.query_pipeline.generate_answer",
        lambda *_args, **_kwargs: "Check the pump seal weekly.",
    )

    result = run_query_pipeline(
        "How do I maintain the pump?",
        vector_store=FakeVectorStore(),  # type: ignore[arg-type]
        settings=Settings(openai_api_key="test-key", chat_model="gpt-4o-mini"),
    )

    assert isinstance(result, QueryPipelineResult)
    assert result.query == "How do I maintain the pump?"
    assert result.answer == "Check the pump seal weekly."
    assert result.confidence_score == pytest.approx(89.3, rel=1e-2)
    assert len(result.citations) == 2
    assert result.citations[0].document_name == "manual.pdf"
    assert result.citations[0].page_number == 1
    assert len(result.chunks) == 2
    assert result.chunks[0].chunk_id == "manual.pdf_p1_abcd1234"

from backend.services.confidence import compute_confidence_score
from src.ingestion.schemas import SearchResult


def test_compute_confidence_score_with_matches() -> None:
    matches = [
        SearchResult("c1", "text", "manual.pdf", 1, 0.25),
        SearchResult("c2", "text", "manual.pdf", 2, 0.75),
    ]
    assert compute_confidence_score(matches) == 80.0


def test_compute_confidence_score_without_matches() -> None:
    assert compute_confidence_score([]) == 0.0

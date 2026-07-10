from __future__ import annotations

from src.ingestion.schemas import SearchResult


def compute_confidence_score(matches: list[SearchResult]) -> float:
    """Convert vector distance scores into a 0-100 confidence percentage."""
    if not matches:
        return 0.0

    best_score = min(match.score for match in matches)
    return round(100.0 / (1.0 + best_score), 1)

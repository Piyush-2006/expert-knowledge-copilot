from __future__ import annotations

from typing import Any

import httpx


class APIError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, f"{self.base_url}{path}", **kwargs)
        except httpx.ConnectError as exc:
            raise APIError(
                f"Cannot reach backend at {self.base_url}. Start it with: "
                "uvicorn backend.main:app --reload",
            ) from exc
        except httpx.TimeoutException as exc:
            raise APIError("Backend request timed out. Try again.") from exc

        if response.status_code >= 400:
            detail = response.json().get("detail", response.text) if response.content else response.text
            raise APIError(str(detail), status_code=response.status_code)

        if not response.content:
            return {}
        return response.json()

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def upload_pdf(self, filename: str, file_bytes: bytes) -> dict[str, Any]:
        return self._request(
            "POST",
            "/upload",
            files={"file": (filename, file_bytes, "application/pdf")},
        )

    def query(self, query: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/query",
            json={"query": query},
        )

    def list_documents(self) -> dict[str, Any]:
        return self._request("GET", "/documents")

    def delete_document(self, document_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/document/{document_id}")

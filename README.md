# Expert Knowledge Copilot

Expert Knowledge Copilot is an AI-powered assistant for industrial knowledge retrieval, guided troubleshooting, and expert decision support.

## Features

- PDF ingestion with `pypdf` text extraction
- OCR fallback via `pytesseract` for scanned pages
- LangChain text chunking with page-level metadata
- ChromaDB vector storage with OpenAI embeddings
- FastAPI backend with upload, query, and document management APIs
- Streamlit frontend with chat UI, citations, and document sidebar

## Prerequisites

- Python 3.11+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and on `PATH`
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/) on `PATH` (required by `pdf2image` on Windows)
- OpenAI API key

## Setup

```powershell
cd "C:\Users\Piyush Kumar\Desktop\industrial-knowledge-copilot"

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -e .

copy .env.example .env
# Edit .env and set OPENAI_API_KEY
```

Optional on Windows if Tesseract is not on PATH:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## Run the backend

```powershell
uvicorn backend.main:app --reload
```

Open:

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Run the frontend

In a second terminal:

```powershell
streamlit run frontend/app.py
```

Open:

- Frontend UI: http://127.0.0.1:8501

Optional: set a custom backend URL before launching Streamlit:

```powershell
$env:API_BASE_URL="http://127.0.0.1:8000"
streamlit run frontend/app.py
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/upload` | Upload and ingest a PDF |
| `POST` | `/query` | Semantic search + optional answer generation |
| `GET` | `/documents` | List ingested documents |
| `DELETE` | `/document/{id}` | Delete a document and its chunks |

### Upload a PDF

```powershell
curl -X POST "http://127.0.0.1:8000/upload" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@C:\path\to\document.pdf"
```

### Query knowledge

```powershell
curl -X POST "http://127.0.0.1:8000/query" `
  -H "Content-Type: application/json" `
  -d "{\"query\": \"How do I maintain the pump?\"}"
```

Example response:

```json
{
  "query": "How do I maintain the pump?",
  "answer": "Check the pump seal weekly.",
  "confidence_score": 89.3,
  "citations": [
    {"document_name": "manual.pdf", "page_number": 1}
  ],
  "chunks": [
    {
      "chunk_id": "manual.pdf_p1_abcd1234",
      "content": "Pump maintenance steps",
      "document_name": "manual.pdf",
      "page_number": 1,
      "relevance_score": 0.12
    }
  ]
}
```

### List documents

```powershell
curl "http://127.0.0.1:8000/documents"
```

### Delete a document

```powershell
curl -X DELETE "http://127.0.0.1:8000/document/manual.pdf"
```

## Run PDF ingestion from CLI

```powershell
ingest-pdf "C:\path\to\document.pdf"
```

Or:

```powershell
python -m src.cli.ingest_pdf "C:\path\to\document.pdf"
```

## Run tests

```powershell
pytest
```

## Project layout

```text
backend/
  main.py              # FastAPI entrypoint
  routes/              # upload, query, documents, health
frontend/
  app.py               # Streamlit entrypoint
  components/          # API client, chat, sidebar, theme
src/
  ingestion/           # PDF read, chunk, embed, store
  core/                # App configuration
docs/                  # Architecture and planning docs
tests/                 # Unit tests
```

## Planning documents

- `docs/architecture-plan.md`
- `docs/database-schema.md`
- `docs/api-endpoints.md`
- `docs/development-roadmap.md`

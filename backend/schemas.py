from __future__ import annotations

from pydantic import BaseModel, Field


##########################################################
# Generic
##########################################################

class ErrorResponse(BaseModel):
    detail: str


##########################################################
# Health
##########################################################

class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str


##########################################################
# Upload
##########################################################

class UploadResponse(BaseModel):
    filename: str
    page_count: int
    chunk_count: int
    ocr_page_count: int
    document_id: str = Field(
        description="Document identifier"
    )


##########################################################
# Query
##########################################################

class QueryRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=4000,
    )


##########################################################
# Citation
##########################################################

class Citation(BaseModel):
    document_name: str
    page_number: int
    source_text: str | None = None


##########################################################
# Retrieved Chunks
##########################################################

class RetrievedChunk(BaseModel):
    chunk_id: str
    content: str
    document_name: str
    page_number: int
    relevance_score: float


##########################################################
# Query Response
##########################################################

class QueryResponse(BaseModel):
    query: str
    answer: str

    confidence_score: float = Field(
        ge=0,
        le=100,
        description="Confidence percentage",
    )

    confidence_level: str = Field(
        description="High / Medium / Low"
    )

    processing_time: float = Field(
        description="Seconds"
    )

    citations: list[Citation]

    chunks: list[RetrievedChunk] = Field(
        description="Top retrieved chunks"
    )


##########################################################
# Documents
##########################################################

class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunk_count: int
    page_numbers: list[int]


class DocumentsResponse(BaseModel):
    documents: list[DocumentInfo]
    total: int


class DeleteDocumentResponse(BaseModel):
    document_id: str
    deleted_chunks: int


##########################################################
# Benchmark
##########################################################

class BenchmarkResponse(BaseModel):
    retrieval_accuracy: float
    citation_accuracy: float
    average_response_time: float


##########################################################
# Knowledge Graph
##########################################################

class GraphNode(BaseModel):
    id: str


class GraphEdge(BaseModel):
    source: str
    target: str


class KnowledgeGraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
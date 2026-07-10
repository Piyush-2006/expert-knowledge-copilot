from pydantic import BaseModel, Field


class IngestionResponse(BaseModel):
    filename: str
    page_count: int
    chunk_count: int
    ocr_page_count: int = Field(description="Number of pages processed with OCR fallback")

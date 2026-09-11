from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PageText(BaseModel):
    page_number: int
    text: str
    extraction_method: str


class DocumentTextExtractionResult(BaseModel):
    filename: str
    page_count: int
    pages: List[PageText]


class ExtractedField(BaseModel):
    value: Any = None
    confidence: Optional[float] = None
    evidence: Optional[str] = None
    page_number: Optional[int] = None


class ExtractionResult(BaseModel):
    document_type: str
    fields: Dict[str, Any]
    tables: List[Dict[str, Any]] = []
    raw_text: Optional[str] = None
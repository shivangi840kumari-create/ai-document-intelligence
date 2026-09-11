from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    document_type: str
    status: str
    validation_status: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    financial_validation: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True
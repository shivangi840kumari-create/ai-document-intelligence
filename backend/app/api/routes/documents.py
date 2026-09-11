import json
from enum import Enum

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.document_repository import (
    get_document,
    get_documents,
    search_document,
)
from app.services.document_service import process_document
from app.services.document_validation_service import validate_document


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)


# Allowed financial document types
class DocumentType(str, Enum):
    INVOICE = "invoice"
    BALANCE_SHEET = "balance_sheet"
    PROFIT_LOSS = "profit_loss"
    CASH_FLOW = "cash_flow"


@router.post("/process")
async def process_uploaded_document(
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate uploaded file
    await validate_document(file)

    # Convert Enum to string before sending to service
    return process_document(
        db=db,
        file=file,
        document_type=document_type.value
    )


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    documents = get_documents(db)

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "document_type": d.document_type,
            "status": d.status,
            "validation_status": d.validation_status,
            "created_at": d.created_at
        }
        for d in documents
    ]


# IMPORTANT:
# Keep this route BEFORE /{document_id}
@router.get("/search/by-name")
def search_by_name(
    filename: str,
    db: Session = Depends(get_db)
):
    documents = search_document(db, filename)

    return [
        {
            "id": d.id,
            "filename": d.filename,
            "document_type": d.document_type,
            "status": d.status,
            "created_at": d.created_at
        }
        for d in documents
    ]


@router.get("/{document_id}")
def get_document_by_id(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = get_document(db, document_id)

    if not document:
        return {"error": "Document not found"}

    return {
        "id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "status": document.status,
        "validation_status": document.validation_status,
        "extracted_data": (
            json.loads(document.extracted_json)
            if document.extracted_json
            else None
        ),
        "financial_validation": (
            json.loads(document.validation_json)
            if document.validation_json
            else None
        ),
        "created_at": document.created_at
    }
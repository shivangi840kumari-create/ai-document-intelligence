import json
from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
    db: Session,
    filename: str,
    document_type: str,
    status: str,
    extracted_data: dict,
    validation_data: dict
):
    document = Document(
        filename=filename,
        document_type=document_type,
        status=status,
        validation_status=validation_data.get("overall_status"),
        extracted_json=json.dumps(extracted_data),
        validation_json=json.dumps(validation_data)
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_documents(db: Session):
    return (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_document(db: Session, document_id: int):
    return (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )


def search_document(db: Session, filename: str):
    return (
        db.query(Document)
        .filter(Document.filename.ilike(f"%{filename}%"))
        .order_by(Document.created_at.desc())
        .all()
    )
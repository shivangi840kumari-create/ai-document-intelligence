import os
import tempfile

from app.repositories.document_repository import create_document
from app.services.ocr_service import extract_text
from app.services.extraction_service import extract_document
from app.services.financial_validation_service import validate_financial_data
from app.services.ai_extraction_service import extract_with_gemini
from app.core.config import settings


def _values_only(fields: dict) -> dict:
    """
    Gemini returns fields like:

    "total": {
        "value": 1500,
        "confidence": 0.98,
        "evidence": "Total 1500",
        "page_number": 1
    }

    Financial validation needs:

    "total": 1500

    This function converts the first format into the second.
    """

    result = {}

    for key, value in fields.items():

        if isinstance(value, dict) and "value" in value:
            result[key] = value.get("value")

        else:
            result[key] = value

    return result


def process_document(db, file, document_type):

    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp:

        temp.write(file.file.read())
        temp_path = temp.name

    try:

        # --------------------------------
        # STEP 1: OCR / TEXT EXTRACTION
        # --------------------------------

        text_result = extract_text(temp_path)

        full_text = "\n".join(
            page["text"]
            for page in text_result["pages"]
        )

        # --------------------------------
        # STEP 2: AI EXTRACTION
        # --------------------------------

        if settings.GEMINI_API_KEY:

            try:

                extracted = extract_with_gemini(
                    document_type=document_type,
                    pages=text_result["pages"]
                )

            except Exception as exc:

                print(
                    "Gemini extraction failed."
                )

                print(
                    "Using rule-based fallback:",
                    exc
                )

                extracted = extract_document(
                    document_type,
                    full_text
                )

        else:

            extracted = extract_document(
                document_type,
                full_text
            )

        # --------------------------------
        # STEP 3: PREPARE VALUES
        # FOR FINANCIAL VALIDATION
        # --------------------------------

        validation_fields = _values_only(
            extracted.get("fields", {})
        )

        # --------------------------------
        # STEP 4: FINANCIAL VALIDATION
        # --------------------------------

        validation = validate_financial_data(
            document_type,
            validation_fields
        )

        status = validation["overall_status"]

        # --------------------------------
        # STEP 5: SAVE TO DATABASE
        # --------------------------------

        document = create_document(
            db=db,
            filename=file.filename,
            document_type=document_type,
            status=status,
            extracted_data=extracted,
            validation_data=validation
        )

        # --------------------------------
        # STEP 6: RETURN RESULT
        # --------------------------------

        return {

            "id": document.id,

            "filename": document.filename,

            "document_type": document.document_type,

            "status": status,

            "extracted_data": extracted,

            "financial_validation": validation,

            "pages": text_result["pages"]
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)
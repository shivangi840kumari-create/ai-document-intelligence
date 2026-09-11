from pathlib import Path

import fitz
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import settings


ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


async def validate_document(file: UploadFile) -> dict:
    # 1. Check filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = Path(file.filename).suffix.lower()

    # 2. Check file extension
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only PDF, JPG, JPEG and PNG are allowed."
        )

    # 3. Read file
    content = await file.read()

    # 4. Check empty file
    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # 5. Check file size
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {settings.MAX_FILE_SIZE_MB} MB limit."
        )

    # Reset file pointer
    await file.seek(0)

    # 6. Validate PDF
    if extension == ".pdf":

        try:
            document = fitz.open(stream=content, filetype="pdf")

            page_count = len(document)

            if page_count == 0:
                document.close()

                raise HTTPException(
                    status_code=400,
                    detail="PDF contains no pages."
                )

            if page_count > settings.MAX_PAGES:
                document.close()

                raise HTTPException(
                    status_code=400,
                    detail=f"PDF contains {page_count} pages. Maximum allowed is {settings.MAX_PAGES} pages."
                )

            # Try reading every page to detect corrupted PDFs
            for page_number in range(page_count):
                document[page_number].get_text("text")

            document.close()

        except HTTPException:
            raise

        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted PDF file."
            )

    # 7. Validate JPG / JPEG / PNG
    else:

        try:
            image = Image.open(file.file)

            # Verify image integrity
            image.verify()

        except (UnidentifiedImageError, OSError, ValueError):
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted image file."
            )

        finally:
            await file.seek(0)

    # 8. Return validation information
    result = {
        "filename": file.filename,
        "extension": extension,
        "size_bytes": len(content),
        "valid": True
    }

    if extension == ".pdf":
        result["page_count"] = page_count
    else:
        result["page_count"] = 1

    return result
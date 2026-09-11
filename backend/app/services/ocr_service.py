from pathlib import Path
from typing import List

import fitz
import pytesseract

from PIL import Image


def extract_from_pdf(file_path: str) -> List[dict]:

    pages = []

    document = fitz.open(file_path)

    for index, page in enumerate(document):

        text = page.get_text("text").strip()

        if text:
            pages.append({
                "page_number": index + 1,
                "text": text,
                "extraction_method": "native_pdf"
            })
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            ocr_text = pytesseract.image_to_string(image)

            pages.append({
                "page_number": index + 1,
                "text": ocr_text.strip(),
                "extraction_method": "tesseract_ocr"
            })

    document.close()

    return pages


def extract_from_image(file_path: str) -> List[dict]:

    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return [{
        "page_number": 1,
        "text": text.strip(),
        "extraction_method": "tesseract_ocr"
    }]


def extract_text(file_path: str) -> dict:

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":

        pages = extract_from_pdf(file_path)

    elif extension in [".jpg", ".jpeg", ".png"]:

        pages = extract_from_image(file_path)

    else:

        raise ValueError("Unsupported file type.")

    return {
        "filename": Path(file_path).name,
        "page_count": len(pages),
        "pages": pages
    }
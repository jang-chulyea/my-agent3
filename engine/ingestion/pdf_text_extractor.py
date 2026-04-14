from engine.input.pdf_loader import extract_text_from_pdf


def extract_text(pdf_path: str) -> str:
    """Extract selectable text from a PDF file.

    OCR is intentionally not implemented here. This wrapper assumes the source
    PDF already contains selectable text.
    """

    return extract_text_from_pdf(pdf_path)

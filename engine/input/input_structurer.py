from engine.input.ocr_loader import extract_text_from_image
from engine.input.pdf_loader import extract_text_from_pdf
from engine.problem_parser.llm_structurer import structure


def structure_input(input_type: str, value: str) -> dict:
    if input_type == "image":
        text = extract_text_from_image(value)
    elif input_type == "pdf":
        text = extract_text_from_pdf(value)
    else:
        text = value

    return structure(text)
